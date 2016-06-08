
import threading
import networkx as nx
import pylab

class Plotter():

    def __init__(self):
        self._lock = threading.Lock()
        self._graph = None

    def start(self):
        plotter_thread = threading.Thread(target=self.plotter)
        plotter_thread.setDaemon(True)
        plotter_thread.setName('plotter')
        plotter_thread.start()

    def updateGraph(self, newGraph):
        self._lock.acquire()
        try:
            self._graph = newGraph
        finally:
            self._lock.release()

    def plotter(self):
        while(True):
            graph = None
            pos = None
            colors = None

            self._lock.acquire()
            try:
                if(self._graph is not None):
                    # everything operating on self._graph must be done under this lock
                    # however, showing the window musn't be done here, because'll block whole application
                    # ending up with the same what we had

                    g = self._graph
                    
                    prod = []
                    cons = []
                    graph = nx.DiGraph()
                    for key in g:
                        for key2 in g[key]:
                            if g[key][key2] > 0:
                                graph.add_edges_from([(key, key2)], weight=g[key][key2])
                                prod.append(key)
                                cons.append(key2)

                    pos = nx.spring_layout(graph)

                    edge_labels=dict([((u, v,), d['weight']) for u, v, d in graph.edges(data=True)])
                    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
                    colors = [1.0 if i in prod else 0.0 for i in graph.nodes()]
            finally:
                self._lock.release()

            if(graph is not None and pos is not None and colors is not None):
                nx.draw(graph, pos, node_color=colors)
                pylab.show(block=True)