import networkx as nx

import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.cm as cmx


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
            g.add_node(equalizer, demand=production - consumption)
            for node, demand in lsdb.demands.iteritems():
                if demand < 0:
                    g.add_edge(node, equalizer, weight=equalizer_cost)
        elif consumption > production:
            g.add_node(equalizer, demand=production - consumption)
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

        flow_cost -= abs(production - consumption) * equalizer_cost

        if equalizer in flow_dict:
            del flow_dict[equalizer]

        for node in flow_dict.values():
            if equalizer in node:
                del node[equalizer]

        return flow_cost, flow_dict

    @staticmethod
    def present_flow(flow_dict, lsdb):
        prodUsed = []
        prodNotFullyUsed = []
        demandZero = []
        consFull = []
        consNotFull = []
        graph = nx.DiGraph()
        for key in flow_dict:
            for key2 in flow_dict[key]:
                if flow_dict[key][key2] > 0:
                    graph.add_edges_from([(key, key2)], weight=flow_dict[key][key2])

        for node in graph.nodes():
            if lsdb[node].demand < 0:
                energy = 0
                for rec in flow_dict[node]:
                    energy += flow_dict[node][rec]
                if energy + lsdb[node].demand >= 0:
                    prodUsed.append(node)
                else:
                    prodNotFullyUsed.append(node)
            elif lsdb[node].demand > 0:
                energy = 0
                for rec in flow_dict:
                    try:
                        energy += flow_dict[rec][node]
                    except:
                        pass
                if energy >= lsdb[node].demand:
                    consFull.append(node)
                else:
                    consNotFull.append(node)
            else:
                demandZero.append(node)

        pos = nx.spring_layout(graph)

        val_map = {}
        for node in prodUsed:
            val_map[node] = 1
        for node in prodNotFullyUsed:
            val_map[node] = 2
        for node in demandZero:
            val_map[node] = 3
        for node in consFull:
            val_map[node] = 4
        for node in consNotFull:
            val_map[node] = 5
        colorLegend = {'Used producers': 1, 'Not fully used producers': 2, 'With zero demand': 3,
                       'Satisfied consumers': 4, 'Not satisfied consumers': 5}

        values = [val_map.get(node, 0) for node in graph.nodes()]
        jet = cm = plt.get_cmap('jet')
        cNorm = col.Normalize(vmin=0, vmax=max(values))
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

        f = plt.figure(1)
        ax = f.add_subplot(1, 1, 1)
        for label in colorLegend:
            ax.plot([0], [0], color=scalarMap.to_rgba(colorLegend[label]), label=label)
        nx.draw_networkx(graph, pos, cmap=jet, vmin=0, vmax=max(values), node_color=values, with_labels=True, ax=ax)

        edge_labels = dict([((u, v,), d['weight']) for u, v, d in graph.edges(data=True)])
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

        plt.axis('off')
        f.set_facecolor('w')
        plt.legend()
        f.tight_layout()
        plt.show()
