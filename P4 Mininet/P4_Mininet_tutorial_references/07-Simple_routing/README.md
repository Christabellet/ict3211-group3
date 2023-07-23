## Tutorial Link: https://github.com/nsg-ethz/p4-learning/tree/master/exercises/08-Simple_Routing/thrift
#### This tutorial main objective is to implement a control plane that is dynamic instead of manually specifying each forwarding table statically. 
#### For this tutorial reference, we break down the routing-controller.py instead of the everything as it is a copy of the ECMP tutorial except for this python file replacing the static sw-commands.txt files. So this python file is what we will be focusing on, for this tutorial. 
## Packet Tracer Topology
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/5bdf03fb-1712-4691-8702-b5e8db7783f8)
## P4 Mininet
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/95d7d9a4-d309-4178-8bf0-d1676e0c22af)
#### Here we can see that the ping request and reply from both h1 and h2 are able to reach each other after running the routing controller python file. This python file is to provide a control plane dynamically instead of manually declaring the forwarding table using sw-commands.txt files. 
### [Routing-controller.py](https://github.com/PototoPatata/ict3211-group3/blob/main/P4%20Mininet/P4_Mininet_tutorial_references/07-Simple_routing/routing-controller.py)
```
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
```
Two helper libraries, `load_topo` load the network topology, `SimpleSwitchThriftAPI` communicates with the P4 switches. 
```
def __init__(self):
	self.topo = load_topo('topology.json')
	self.controllers = {}
	self.init()
```
`self.topo = load_topo('topology.json')` initialise the routing controller by loading the network topology, in this case it loads `topology.json`. `self.controller = {}` initialise a empty dictionary for controller object for each P4 switch. `self.init()` is a method being called at the end of initialisation. 
```
def init(self):
	self.connect_to_switches()
	self.reset_states()
	self.set_table_defaults()
```
`self.connect_to_switches()` connects the P4 switch in the network, `self.reset_states()` reset their state back to normal, `self.set_table_defaults()` set the default action for the tables as `drop`. 
```
def reset_states(self):
	[controller.reset_state() for controller in self.controllers.values()]
```
When this function is called, it resets the state of all controllers for P4 switch. 
```
def connect_to_switches(self):
	for p4switch in self.topo.get_p4switches():
		thrift_port = self.topo.get_thrift_port(p4switch)
		self.controllers[p4switch] = SimpleSwitchThriftAPI(thrift_port)
```
This function iterates over all P4 switches, fetch the Thrift port for each switch, and creates a `SimpleSwitchThriftAPI` instances to store in the `self.controllers = {}` dictionary. 
```
def set_table_defaults(self):
	for controller in self.controllers.values():
		controller.table_set_default("ipv4_lpm", "drop", [])
		controller.table_set_default("ecmp_group_to_nhop", "drop", [])
```
When this function is called, it sets the default rule on all P4 switch's table to `drop` packet. 
```
def route(self):
```
This function is where the routing tables for each switch are defined. Which is split into two main parts, setting up direct connection and setting up routing to other switches. The following will be a breakdown for each small section for ease of understanding. 
```
switch_ecmp_groups = {sw_name:{} for sw_name in self.topo.get_p4switches().keys()}
```
This line initializes a dictionary for each switch, `sw_name` will dynamically call the name of each switch. 
```
for sw_name, controller in self.controllers.items():
```
This loop iterates over each switch and its controller. 
```
if sw_name == sw_dst:
```
This line checks if the current switch is the destination switch. If it is, it handles setting up the connection to hosts. 
```
sw_port = self.topo.node_to_node_port_num(sw_name, host)
host_ip = self.topo.get_host_ip(host) + "/32"
host_mac = self.topo.get_host_mac(host)
```
These lines get the port number for the host, the host's IP address, and the host's MAC address. 
```
self.controllers[sw_name].table_add("ipv4_lpm", "set_nhop", [str(host_ip)], [str(host_mac), str(sw_port)])
```
This adds a rule to the switch's IPv4 Longest Prefix Match (`ipv4_lpm`) table, setting the next hop (`set_nhop`) to the host. The parameters to the rule are the host's IP (`str(host_ip`), MAC (`str(host_mac)`), and port (`str(sw_port)`).
```
if self.topo.get_hosts_connected_to(sw_dst):
```
This line checks if there is any host directly connected to the destination switch. 
```
paths = self.topo.get_shortest_paths_between_nodes(sw_name, sw_dst)
```
This line gets the shortest path to the destination switch from the current switch. 
```
if len(paths) == 1:
elif len(paths) > 1:
```
The first line checks if the there is only a single shortest path, while the second line checks if there is more than one shortest path. 
```
switch_ecmp_groups[sw_name][tuple(dst_macs_ports)] = new_ecmp_group_id
```
If the shortest path is more than one and ECMP group does not exist. This line will add a new ECMP group to the dictionary for the current switch. 
```
for i, (mac, port) in enumerate(dst_macs_ports):
```
This line iterates over each next hop to add the ECMP group to the ```ecmp_group_to_nhop``` table for each switch. 
```
self.controllers[sw_name].table_add(
	"ipv4_lpm", 
	"ecmp_group", 
	[str(host_ip)], 
	[str(new_ecmp_group_id), 
	str(len(dst_macs_ports))])
```
This line adds the forwarding rule to the switch `ipv4_lpm` table to use the ECMP group for the host's IP address. 
