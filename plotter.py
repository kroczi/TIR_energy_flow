import networkx as nx

import matplotlib.pyplot as plt


class Plotter():
    def __init__(self, router):
        self._router = router

    def present_flow(self):
        ef = self._router.get_energy_flow()
        if ef is not None:
            Plotter._present_flow(ef)

    @staticmethod
    def _present_flow(flow_dict):
        graph = nx.DiGraph()
        for key in flow_dict:
            for key2 in flow_dict[key]:
                if flow_dict[key][key2] > 0:
                    graph.add_edge(key, key2)

        pos = nx.spring_layout(graph)
        nx.draw(graph, pos)
        plt.show()
