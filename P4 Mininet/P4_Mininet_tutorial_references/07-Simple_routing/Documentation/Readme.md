## Explanation of Code
#### The objective of this exercise is to implement a control plane that generates and installs forwarding rules automatically based on the network topology diagram.

In this exercise, you would require 3 files as shown below, 
| File | Description |
| --- | --- |
| `p4app.json` | creates the topology of the network diagram |
| `routing-controller.p4` |routing controller that is used to populate routing tables.|
| `ecmp.p4` | p4 program that defines how packets should flow in a network diagram |

The ecmp.p4 file used is the same as the previous ECMP exercise. 

In the routing-controller.py file,

The main method for configuring the routing rules is the method `route(self)`. 
```
switch_ecmp_groups = {sw_name:{} for sw_name in self.topo.get_p4switches().keys()}
```
The method starts by creating a dictionary `switch_ecmp_groups` to store ECMP groups for each switch. It initialises an empty dictionary for each switch in the network.  
```
        for sw_name, controller in self.controllers.items():
            for sw_dst in self.topo.get_p4switches():
```
The nested loop iterates through each switch in the network and then iterates through all the switches again as `sw_dst`.
```
if sw_name == sw_dst:
```
The if statement checks if the source switch is the same as the destination switch. Then it will create direct connections between the switch and the host connected to it.
```
                    for host in self.topo.get_hosts_connected_to(sw_name):
                        sw_port = self.topo.node_to_node_port_num(sw_name, host)
                        host_ip = self.topo.get_host_ip(host) + "/32"
                        host_mac = self.topo.get_host_mac(host)
```
This command iterates through the host connected to the switch. It retrieves the switch port number connected to the host, the host’s IP address and MAC address. 
```
 print("table_add at {}:".format(sw_name))
                        self.controllers[sw_name].table_add("ipv4_lpm", "set_nhop", [str(host_ip)], [str(host_mac), str(sw_port)])
```
It then adds a rule to the `ipv4_lpm` table of the switch that forwards packets destined for that host’s IP address to the corresponding MAC address and port number. 
```
                else:
                    if self.topo.get_hosts_connected_to(sw_dst):
                        paths = self.topo.get_shortest_paths_between_nodes(sw_name, sw_dst)
                        for host in self.topo.get_hosts_connected_to(sw_dst):
```
If the `sw_dst` is not the same as the `sw_name`, it indicates that there is no direct connection and there is a need for routing packets from `sw_name` to another switch to reach the host connected to `sw_dst` .  

The command `paths = self.topo.get_shortest_paths_between_nodes(sw_name, sw_dst)` indicates that it retrieves the shortest path between the source switch and the destination switch using the g`et_shortest_paths_between_nodes` function. 
```
                            if len(paths) == 1:
                                next_hop = paths[0][1]
                                host_ip = self.topo.get_host_ip(host) + "/24"
                                sw_port = self.topo.node_to_node_port_num(sw_name, next_hop)
                                dst_sw_mac = self.topo.node_to_node_mac(next_hop, sw_name)
```
If the length of the path equals to 1, the controller would set up a routing table in the `ipv4_lpm` table to forward packets destined for hosts connected to `sw_dst` through the next hop switch. 
```
                            elif len(paths) > 1:
                                next_hops = [x[1] for x in paths]
                                dst_macs_ports = [(self.topo.node_to_node_mac(next_hop, sw_name),
                                                   self.topo.node_to_node_port_num(sw_name, next_hop))
                                                  for next_hop in next_hops]
                                host_ip = self.topo.get_host_ip(host) + "/24"
                                else:
                                    new_ecmp_group_id = len(switch_ecmp_groups[sw_name]) + 1
                                    switch_ecmp_groups[sw_name][tuple(dst_macs_ports)] = new_ecmp_group_id

                                    #add group
                                    for i, (mac, port) in enumerate(dst_macs_ports):
                                        print("table_add at {}:".format(sw_name))
                                        self.controllers[sw_name].table_add("ecmp_group_to_nhop", "set_nhop",
                                                                            [str(new_ecmp_group_id), str(i)],
                                                                            [str(mac), str(port)])
```
This condition is when there are multiple paths needed from the source switch to the destination switch, indicating the need for ECMP routing. The code fetches the next hop switches and their corresponding MAC addresses and ports along each path. It then checks if an ECMP group for these hops already existed. If yes, it will use the existing ECMP group ID, otherwise it will create a new ECMP group for the switch and add the forwarding rules accordingly. 
