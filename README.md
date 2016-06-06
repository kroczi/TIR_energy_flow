# IOT Energy Flow

A simulation of energy flow from electricity providers to end nodes in an iot devices network. Implemented basing on OSPF mechanisms and network simplex algorithm for finding minimal cost flow in the graph.

## Usage
    python main.py <path to router cfg file>

## Dependencies
1. [Python](http://www.python.org/download/) >= 2.5
2. [PyQt](http://www.riverbankcomputing.com/software/pyqt/download) >= 4.4
3. [NetworkX](https://networkx.github.io/documentation/networkx-1.9.1/index.html)


## Simulation Constraints

### LSA Type
* All transmitted and received LSAs are Router LSAs

### Router IDs
* The Router ID (RID) used is simply the hostname of a router instead of the IP address of a router's interface. Must be unique.

### Link ID
* Must be unique.

### Link Cost
* Maximum of the cost values from both of its ends

### Link Capacity
* Minimum of the capacity values from both of its ends

## Program Design

### OSPF Architectural Constants

Most of the essential architectural constants of OSPF have been taken into account. This includes the Hello and Dead intervals, Age interval, LS Refresh time, and Max Age. Since the Age interval, LS Refresh time, and Max Age are in the minute-to-hour range, a time scaling factor was introduced. However, the Hello and Dead intervals were not scaled anymore because both of them are only under a minute. The scaling factor, which can be easily changed, defaults to 20 so that 1 minute (60 seconds) would only be 3 seconds in actuality.

### Router Communications

UDP Multicast. Router determines whether it is interested in a packet based on packet link_id.

### Router Configuration

The program code need not be changed for each simulated router. The information needed to simulate a router is separately stored in a router configuration file. The configuration file specifies the router's hostname, energy demand, energy links and their ids, costs, and capacities. One can simulate any network topology by carefully assigning the correct interconnections between routers.

```
[Router]
hostname = Router1
demand = 5

[Link1]
link = 1
cost = 8
capacity = 14

[Link2]
link = 2
cost = 4
capacity = 22

```

