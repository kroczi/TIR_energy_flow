# -*- coding: utf-8 -*-
# Copyright (c) 2009 Darwin M. Bautista
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import networkx as nx
import matplotlib.pyplot as plt
import pylab

TIME_SCALE = 20  # 1 minute (60 seconds) is to 3 seconds (60 / 3 = 20)


def _scale_time(minutes):
    return 60.0 * minutes / TIME_SCALE


BANDWIDTH_BASE = 100000000  # 100 Mbps
HELLO_INTERVAL = 10  # 10 seconds
DEAD_INTERVAL = 4 * HELLO_INTERVAL  # typical value is 4 times the HELLO_INTERVAL
AGE_INTERVAL = _scale_time(1)  # 1 minute
LS_REFRESH_TIME = _scale_time(30)  # 30 minutes
MAX_AGE = _scale_time(60)  # 1 hour


class LinkStatePacket(object):
    def __init__(self, router_id, demand, age, seq_no, networks):
        self.adv_router = router_id
        self.link = ""
        self.demand = demand
        self.age = age
        self.seq_no = seq_no
        self.networks = networks

    def __repr__(self):
        stat = '\nADV Router: %s\nDemand: %d\nAge: %d\nSeq No.: %d\nNetworks: %s\n\n' % (
            self.adv_router, self.demand, self.age, self.seq_no, self.networks)
        return stat


class HelloPacket(object):
    def __init__(self, router_id, seen):
        self.router_id = router_id
        self.link = ""
        self.seen = seen


class AdminPacket(object):
    ADD_LINK = 0
    REMOVE_LINK = 1
    UPDATE_DEMAND = 2
    GENERATE_BREAKDOWN = 3
    RESET_ROUTER = 4

    def __init__(self, action, router_id=None, another_router_id=None,
                 link=None, cost=None, capacity=None, demand=None, filename=None):
        self.action = action
        self.router_id = router_id
        self.another_router_id = another_router_id
        self.link = link
        self.cost = cost
        self.capacity = capacity
        self.demand = demand
        self.filename = filename


class Database(dict):
    def __init__(self):
        dict.__init__(self)
        self.demands = {}

    def insert(self, lsa):
        """Returns True if LSA was added/updated"""
        if lsa.adv_router not in self or lsa.seq_no > self[lsa.adv_router].seq_no:
            self[lsa.adv_router] = lsa
            self.demands[lsa.adv_router] = lsa.demand
            return True
        else:
            return False

    def remove(self, router_id):
        """Remove LSA from router_id"""
        if router_id in self:
            del self[router_id]
            del self.demands[router_id]

    def flush(self):
        """Flush old entries"""
        flushed = []
        for router_id in self:
            if self[router_id].age > MAX_AGE:
                flushed.append(router_id)
        map(self.pop, flushed)
        map(self.demands.pop, flushed)
        return flushed

    def update(self):
        """Update LSDB by aging the LSAs and flushing expired LSAs"""
        for adv_router in self:
            self[adv_router].age += 1
        return self.flush()

    def get_flow(self):
        """Return a list of shortest paths from router_id to all other nodes"""
        g = nx.DiGraph()
        production = 0
        consumption = 0

        for node, demand in self.demands.iteritems():
            g.add_node(node, demand=demand)
            if demand > 0:
                consumption += demand
            else:
                production -= demand

        if production > consumption:
            g.add_node('equalizer', demand=production-consumption)
            for node, demand in self.demands.iteritems():
                if demand < 0:
                    g.add_edge(node, 'equalizer', weight=100)
        elif consumption > production:
            g.add_node('equalizer', demand=production-consumption)
            for node, demand in self.demands.iteritems():
                if demand > 0:
                    g.add_edge('equalizer', node, weight=100)

        for lsa in self.values():
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

        flow_cost -= abs(production-consumption)*100

        if 'equalizer' in flow_dict:
            del flow_dict['equalizer']

        for node in flow_dict.values():
            if 'equalizer' in node:
                del node['equalizer']

        prod = []
        cons = []
        graph = nx.DiGraph()
        for key in flow_dict:
            for key2 in flow_dict[key]:
                if flow_dict[key][key2] > 0:
                    graph.add_edges_from([(key, key2)], weight=flow_dict[key][key2])
                    prod.append(key)
                    cons.append(key2)

        pos = nx.spring_layout(graph)

        edge_labels=dict([((u, v,), d['weight']) for u, v, d in graph.edges(data=True)])
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
        colors = [1.0 if i in prod else 0.0 for i in graph.nodes()]

        nx.draw(graph, pos, node_color=colors)
        pylab.show()

        return flow_cost, flow_dict
