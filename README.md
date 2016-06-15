# IOT Energy Flow

A simulation of energy flow from electricity providers to end nodes in an iot devices network. Implemented basing on OSPF mechanisms and network simplex algorithm for finding minimal cost flow in the graph.

## Usage
    python main.py -c <path_to_node_cfg_file> [-I] [-L]
    or
    python main.py -n <node_hostname> [-d <demand>] [-I] [-L]

## Dependencies
1. [Python](http://www.python.org/download/) >= 2.5
2. [NetworkX](https://networkx.github.io/documentation/networkx-1.9.1/index.html)
3. [Matlibplot](http://matplotlib.org/)


## Simulation Constraints

### Node IDs
* As the Node ID is simply used the hostname of the node. Must be unique.

### Node Demand
* Integer that describes the node's need for energy:
 * If demand > 0, then the node produces demand units of energy
 * If demand < 0, then the node consumes -demand units of energy
 * If demand == 0, then node is just a transportation node - it neither produces nor consumes any energy

### Link ID
* Must be unique.

### Link Cost
* Maximum of the cost values from both of its ends

### Link Capacity
* Minimum of the capacity values from both of its ends

## Program Design

### OSPF Architectural Constants

Most of the essential architectural constants of OSPF have been taken into account. This includes the Hello and Dead intervals, Age interval, LS Refresh time, and Max Age. Since the Age interval, LS Refresh time, and Max Age are in the minute-to-hour range, a time scaling factor was introduced. However, the Hello and Dead intervals were not scaled anymore because both of them are only under a minute. The scaling factor, which can be easily changed, defaults to 20 so that 1 minute (60 seconds) would only be 3 seconds in actuality.

### Node Communications

UDP Multicast. Node determines whether it is interested in a packet based on packet Link ID.

### Node Configuration

The program code need not be changed for each simulated node. The information needed to simulate a node is separately stored in a node configuration file. The configuration file specifies the node's hostname, energy demand, energy links and their ids, costs, and capacities. One can simulate any network topology by carefully assigning the correct interconnections between nodes.

```
[Router]
hostname = Node1
demand = 5

[Link1]
link = 1
cost = 8
capacity = 14

[Link2]
link = 3
cost = 4
capacity = 22

```

