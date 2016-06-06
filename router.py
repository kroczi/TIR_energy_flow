from PyQt4 import QtCore

from interface import Interface

try:
    import cPickle as pickle
except ImportError:
    import pickle

import ospf


def mktimer(interval, callback, args=(), single_shot=False):
    t = QtCore.QTimer()
    t.setInterval(1000 * interval)
    if args:
        def timeout():
            callback(*args)
    else:
        timeout = callback
    t.setSingleShot(single_shot)
    QtCore.QObject.connect(t, QtCore.SIGNAL('timeout()'), timeout)
    return t


def log(msg):
    print 'log:', msg


class Router(object):
    def __init__(self, hostname, demand):
        self._hostname = hostname
        self._demand = demand
        self._lsdb = ospf.Database()
        self._links = {}
        self._neighbors = {}
        self._seen = {}
        self._energy_flow = {}
        self._init_timers()
        self._interface = Interface(self)

    def __del__(self):
        self.stop()

    def _init_timers(self):
        log('Init timers.')
        self._dead_timer = None
        self._timers = {'lsdb': mktimer(ospf.AGE_INTERVAL, self._update_lsdb),
                        'refresh_lsa': mktimer(ospf.LS_REFRESH_TIME, self._refresh_lsa),
                        'hello': mktimer(ospf.HELLO_INTERVAL, self._hello)}

    def _update_lsdb(self):
        log('LSDB update.')
        flushed = self._lsdb.update()
        if flushed:
            log('LSA(s) of %s reached MaxAge and was/were flushed from the LSDB' % (', '.join(flushed),))

    def _refresh_lsa(self):
        if self._hostname in self._lsdb:
            log('Refreshing own LSA')
            self._advertise()

    def _hello(self):
        """Establish adjacency"""
        log('Sending HelloPacket.')
        for link, attr in self._links.iteritems():
            packet = ospf.HelloPacket(self._hostname, (link, attr[0], attr[1]))
            self._interface.transmit(packet, link)
        for neighbor_id in self._seen:
            if neighbor_id not in self._neighbors:
                self._sync_lsdb(neighbor_id)

    def _update_energy_flow(self):
        log('Recalculating flow.')
        flow_cost, flow_dict = self._lsdb.get_flow()
        self._energy_flow = flow_dict[self._hostname]
        log(flow_dict[self._hostname])

        # TODO: Display flow in console / on Galileo

    def _break_adjacency(self, neighbor_id):
        log('Break adjacency.')
        # Save reference QObject errors
        self._dead_timer = self._timers[neighbor_id]
        del self._timers[neighbor_id]
        del self._neighbors[neighbor_id]
        del self._seen[neighbor_id]
        log(' '.join([neighbor_id, 'is down']))
        self._advertise()

    def _flood(self, packet, source_link=None):
        """Flood received packet to other interfaces"""
        if packet.adv_router == self._hostname:
            log('Flooding own LSA')
        else:
            log('Flooding LSA of %s' % (packet.adv_router,))

        for data in self._neighbors.values():
            if data[0] != source_link:
                self._interface.transmit(packet, data[0])

    def _advertise(self):
        log('Advertise.')
        networks = {}
        for neighbor_id, data in self._neighbors.iteritems():
            link, cost, capacity = data
            cost = max(cost, self._links[link][0])
            capacity = min(capacity, self._links[link][1])
            networks[link] = (neighbor_id, link, cost, capacity)
        # Create new or update existing LSA
        if self._hostname in self._lsdb:
            lsa = self._lsdb[self._hostname]
            lsa.seq_no += 1
            lsa.age = 1
            lsa.networks = networks
        else:
            lsa = ospf.LinkStatePacket(self._hostname, self._demand, 1, 1, networks)
        self._lsdb.insert(lsa)
        # Flood LSA to neighbors
        self._flood(lsa)
        self._update_energy_flow()

    def _sync_lsdb(self, neighbor_id):
        log('Sync LSDB.')
        topology_changed = (neighbor_id not in self._neighbors)
        if topology_changed:
            log('Adjacency established with %s' % (neighbor_id,))
        self._neighbors[neighbor_id] = self._seen[neighbor_id]
        if self._hostname not in self._lsdb:
            log('Creating initial LSA')
            self._advertise()
        elif topology_changed:
            self._advertise()
            # Sync LSDB with neighbor
            for lsa in self._lsdb.values():
                self._interface.transmit(lsa, self._neighbors[neighbor_id][0])

    def _handle_hello(self, packet):
        neighbor_id = packet.router_id
        if neighbor_id != self._hostname:
            log('Received HelloPacket.')
            log('Seen %s' % (neighbor_id,))

            # Reset Dead timer
            if neighbor_id in self._timers:
                self._timers[neighbor_id].stop()
            t = mktimer(ospf.DEAD_INTERVAL, self._break_adjacency, (neighbor_id,), True)
            t.start()
            self._timers[neighbor_id] = t

            self._seen[neighbor_id] = packet.seen
            if self._hostname in packet.seen:
                self._sync_lsdb(neighbor_id)

    def _handle_lsa(self, packet):
        log('Received LSA.')
        # Insert to Link State database
        if self._lsdb.insert(packet):
            if packet.adv_router == self._hostname:
                self._advertise()
            else:
                log('Received LSA of %s via %s and merged to the LSDB' % (packet.adv_router, packet.link))
                self._flood(packet, packet.link)
                self._update_energy_flow()
        elif packet.adv_router == self._hostname and packet.seq_no == 1:
            self._advertise()

    def start(self):
        log('Start.')
        # Start timers
        for t in self._timers.values():
            t.start()
        self._hello()

    def stop(self):
        log('Stop.')
        for t in self._timers.values():
            t.stop()
        self._interface.handle_close()

    def handle_packet(self, packet):
        if packet.link in self._links:
            if isinstance(packet, ospf.HelloPacket):
                self._handle_hello(packet)
            elif isinstance(packet, ospf.LinkStatePacket):
                self._handle_lsa(packet)

    def add_link(self, link, cost, capacity):
        log("Added link %s." % (link,))
        if link not in self._links:
            self._links[link] = (cost, capacity)

    def remove_link(self, link):
        log("Removed link %s." % (link,))
        if link in self._links:
            del self._links[link]

    def update_demand(self, demand):
        self._demand = demand
        if self._hostname in self._lsdb:
            self._lsdb[self._hostname].demand = demand
            self._advertise()

    def generate_breakdown(self):
        self.stop()

    # TODO: Dynamic link insertion/removal, breakdowns generating or demand change from console/Galileo
    # Probably some second thread in main that listens for input from console/Galileo. Appropriate router methods above.
