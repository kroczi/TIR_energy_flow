import thread
import threading

from ospf import AdminPacket


class EventGenerator(object):
    def __init__(self, router):
        self._router = router

    def add_link(self, router_id, another_router_id, link, cost, capacity):
        self._router.transmit(AdminPacket(AdminPacket.ADD_LINK, router_id=router_id,
                                          another_router_id=another_router_id, link=link,
                                          cost=cost, capacity=capacity), link)

    def remove_link(self, link):
        self._router.transmit(AdminPacket(AdminPacket.REMOVE_LINK, link=link), link)

    def update_demand(self, router_id, demand):
        self._router.transmit(AdminPacket(AdminPacket.UPDATE_DEMAND, router_id=router_id,
                                          demand=demand), None)

    def generate_breakdown(self, router_id):
        self._router.transmit(AdminPacket(AdminPacket.GENERATE_BREAKDOWN, router_id=router_id), None)

    def reset_router(self, router_id, another_router_id=None, demand=None, filename=None):
        self._router.transmit(AdminPacket(AdminPacket.RESET_ROUTER, router_id=router_id,
                                          another_router_id=another_router_id, demand=demand,
                                          filename=filename), None)

    def show_graph(self):
        self._router.show_graph()

    def stop_simulation(self):
        self._router.stop()


class InputThread(threading.Thread):
    def __init__(self, generator):
        super(InputThread, self).__init__()
        self._generator = generator

    def run(self):
        while True:
            value = raw_input().split()

            if len(value) < 1:
                continue
            elif value[0] == "q":
                self._generator.stop_simulation()
                break
            elif value[0] == "al":
                if len(value) != 6:
                    continue
                self._generator.add_link(value[1], value[2], value[3], int(value[4]), int(value[5]))
            elif value[0] == "rl":
                if len(value) != 2:
                    continue
                self._generator.remove_link(value[1])
            elif value[0] == "ud":
                if len(value) != 3:
                    continue
                self._generator.update_demand(value[1], int(value[2]))
            elif value[0] == "gb":
                if len(value) != 2:
                    continue
                self._generator.generate_breakdown(value[1])
            elif value[0] == "rr":
                if len(value) == 3 and value[2].endswith(".cfg"):
                    self._generator.reset_router(value[1], filename=value[2])
                elif len(value) == 3:
                    self._generator.reset_router(value[1], another_router_id=value[2])
                elif len(value) == 4:
                    self._generator.reset_router(value[1], another_router_id=value[2], demand=int(value[3]))

            elif value[0] == "sg":
                self._generator.show_graph()

        thread.interrupt_main()
