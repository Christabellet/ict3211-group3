## Tutorial Link: https://github.com/nsg-ethz/p4-learning/tree/master/exercises/03-L2_Flooding/thrift
#### This tutorial main objective is to implement broadcasting of a unknown destination MAC address packet. 
#### The difference between ```all-port``` and ```other-port``` is that ```all-port``` will broadcast to all port while ```other-port``` will broadcast to all other port except for the sender port which is the correct broadcasting method, as such we will be using ```other-port``` solution. 
## Packet Tracer Topology
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/b00714e8-e533-41ea-92b3-c1bfb6b35281)
## P4 Mininet
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/459017a8-7983-4b49-8608-31cefbfc2c42)
## P4 Switch Thrift Port
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/19609d37-9cb5-4cb0-847a-9247b3da707a)
## Flow Rules
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/f3e407b9-d655-4ccd-8787-5d10dd688da1)
#### The flow rules of the switch will first go through dmac table for forwarding packet based on their destination MAC address. If the packet needs to be broadcasted, as defined in the ```broadcast``` action section of the dmac table, the flow will proceed to the select_mcast_grp table to set the multicast group based on the ingress port. 
## Flow Chart
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/ddd53e1f-6365-4710-9c8f-1462399b3890)
### 1. Parser
```
state start {
	packet.extract(hdr.ethernet);
	transition accept;
}
```
When the P4 switch receives a packet, its parser state will switch to start state and extract the ethernet header from the packet before transitioning to accept mode. 
### 2. Verify Checksum
```No action is taken. ```
### 3. Ingress Processing
```
action forward(bit<9> egress_port) {
	standard_metadata.egress_spec = egress_port;
	}
action broadcast() {
}
```
This ```forward``` action section set the output port for the packet as the egress port parameter of the P4 switch. While the ```broadcast``` action section has no action but will act as a trigger for another table for the flow rule. 
```
table dmac {
	key = {
		hdr.ethernet.dstAddr: exact;
	}
	actions = {
		forward;
		broadcast;
		NoAction;
	}
	size = 256;
	default_action = NoAction;
}
```
Table dmac is defined with a single key field, ```hdr.ethernet.dstAddr```, which represents the destination MAC address of the packet headers being process. The line ```hdr.ethernet.dstAddr: exact;``` meant that the key field is to be matched exactly. The ```actions``` section defines three action that can be taken, ```forward``` which was declared above, ```broadcast``` which was declared above as well, and `NoAction` which by default meant no action to be taken. The table size is set to hold up to 256 entries using `size = 256`. 
```
action set_mcast_grp(bit<16> mcast_grp) {
	standard_metadata.mcast_grp = mcast_grp;
	}
```
This `set_mcast_grp` action section set the multicast group identifier for the egress packet. 
```
table select_mcast_grp {
	key = {
		standard_metadata.ingress_port : exact;
	}
	actions = {
		set_mcast_grp;
		NoAction;
	}
	size = 32;
	default_action =  NoAction;
}
```
Table select_mcast_grp is defined with a single key field, `standard_metadata.ingress_port`, which represents the port where the processing packet was received from. The line `standard_metadata.ingress_port : exact;` meant that the key field is to be matched exactly. The `actions` section defines two actions that can be taken, `set_mcast_grp` which was declared above and `NoAction` which by default meant no action to be taken. The table size is set to hold up to 256 entries using `size = 256`. 
```
apply {
	switch (dmac.apply().action_run) {
		broadcast: {
			select_mcast_grp.apply();
				}
	}
```
The apply block will apply the dmac table to the incoming packet first, if the selected action from the dmac table is `broadcast`, the select_mcast_grp table will be applied. This logic is to allow the selection of multicast group based on ingress port when the packet is not found in the dmac table and needs to be broadcasted. 
### 4. Egress Processing
`No action is taken. `
### 5. Compute Checksum
`No action is taken. `
### 6. Deparser
```
apply {
	packet.emit(hdr.ethernet);
}
```
After extracting the ethernet header to process, the p4 switch need to re-encapsulate the packet with the new ethernet header before the packet egress. 
### 7. Packet Egress
```
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
```
This is the standard packet egress logic flows in the P4 switch, which is also the end state of a packet flow in one direction, where all processing is done and the packet is ready to egress.
