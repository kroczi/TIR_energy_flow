import networkx as nx
import matplotlib.pyplot as plt


class FlowManager(object):

    @staticmethod
    def calculate_flow(lsdb):
        production = 0
        consumption = 0
        equalizer = 'equalizer'
        equalizer_cost = 100

        g = nx.DiGraph()

        for node, demand in lsdb.demands.iteritems():
            g.add_node(node, demand=demand)
            if demand > 0:
                consumption += demand
            else:
                production -= demand

        if production > consumption:
            g.add_node(equalizer, demand=production-consumption)
            for node, demand in lsdb.demands.iteritems():
                if demand < 0:
                    g.add_edge(node, equalizer, weight=equalizer_cost)
        elif consumption > production:
            g.add_node(equalizer, demand=production-consumption)
            for node, demand in lsdb.demands.iteritems():
                if demand > 0:
                    g.add_edge(equalizer, node, weight=equalizer_cost)

        for lsa in lsdb.values():
            for data in lsa.networks.values():
                neighbor_id, link, cost, capacity = data
                g.add_edge(lsa.adv_router, neighbor_id, weight=cost, capacity=capacity)
                g.add_edge(neighbor_id, lsa.adv_router, weight=cost, capacity=capacity)

        flow_cost = 0
        flow_dict = {}
        try:
            flow_cost, flow_dict = nx.network_simplex(g)
        except nx.NetworkXUnfeasible as e:
            pass  # TODO: Handle no flow satisfying all demand (the equalized one).
        except (nx.NetworkXError, nx.NetworkXUnbounded) as e:
            pass  # TODO: Handle not connected graph or a cycle of negative cost and infinite capacity.

        flow_cost -= abs(production-consumption)*equalizer_cost

        if equalizer in flow_dict:
            del flow_dict[equalizer]

        for node in flow_dict.values():
            if equalizer in node:
                del node[equalizer]

        return flow_cost, flow_dict

    @staticmethod
    def present_flow(flow_dict):
        graph = nx.DiGraph()
        for key in flow_dict:
            for key2 in flow_dict[key]:
                if flow_dict[key][key2] > 0:
                    graph.add_edge(key, key2)

        pos = nx.spring_layout(graph)
        nx.draw(graph, pos)
        plt.show()