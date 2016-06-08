import asynchat
import asyncore
import socket
import struct
from errno import EWOULDBLOCK

try:
    import cPickle as pickle
except ImportError:
    import pickle

MCAST_GRP = '236.0.0.0'
MCAST_PORT = 3456

_terminator = '\0E\0O\0F\0'

poll = asyncore.poll


def log(msg):
    print 'log:', msg


class Interface(asyncore.dispatcher):
    """Physical Router interface"""

    def __init__(self, router):
        log('Interface init.')
        asyncore.dispatcher.__init__(self)
        self.router = router
        self.connections = {}
        self.tx = IfaceTx(self.connections)
        self.rx = IfaceRx(self.router, self.connections)
        log('%s up' % (self.router._hostname,))

    @staticmethod
    def writable(self):
        return False

    def handle_start(self):
        self.tx.handle_start()
        self.rx.handle_start()

    def handle_close(self):
        for conn in self.connections.values():
            conn.handle_close()
        self.tx.handle_close()
        self.rx.handle_close()

    def transmit(self, packet, link):
        """Transmit a packet through the interface"""
        packet.link = link
        data = pickle.dumps(packet)
        self.tx.push(''.join([data, _terminator]))


class IfaceTx(asynchat.async_chat):
    ac_in_buffer_size = 0

    def __init__(self, connections):
        log('InterfaceTx init.')
        asynchat.async_chat.__init__(self)
        self.set_socket(self.get_socket())
        self.add_channel(connections)
        self.connections = connections

    def readable(self):
        return False

    @staticmethod
    def get_socket():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        return sock

    def send(self, data):
        try:
            result = self.socket.sendto(data, (MCAST_GRP, MCAST_PORT))
            return result
        except socket.error, why:
            if why.args[0] == EWOULDBLOCK:
                return 0
            elif why.args[0] in asyncore._DISCONNECTED:
                self.handle_close()
                return 0
            else:
                raise

    def handle_error(self):
        self.handle_close()

    def handle_start(self):
        self.connected = True

    def handle_close(self):
        if self._fileno in self.connections:
            del self.connections[self._fileno]
        self.close()


class IfaceRx(asynchat.async_chat):
    ac_out_buffer_size = 0

    def __init__(self, router, connections):
        log('InterfaceRx init.')
        asynchat.async_chat.__init__(self)
        self.set_socket(self.get_socket())
        self.add_channel(connections)
        self.connections = connections
        self.set_terminator(_terminator)
        self.router = router
        self.connections = connections
        self.buffer = []

    @staticmethod
    def get_socket():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((MCAST_GRP, MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        return sock

    def collect_incoming_data(self, data):
        self.buffer.append(data)

    def found_terminator(self):
        data = ''.join(self.buffer)
        self.buffer = []
        # Deserialize packet
        packet = pickle.loads(data)
        self.router.handle_packet(packet)

    def handle_error(self):
        self.handle_close()

    def handle_start(self):
        self.connected = True

    def handle_close(self):
        if self._fileno in self.connections:
            del self.connections[self._fileno]
        self.close()
