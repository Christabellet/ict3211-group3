## Tutorial Link: https://github.com/nsg-ethz/p4-learning/tree/master/exercises/04-L2_Learning/thrift
#### This tutorial main objective is to implement the capability to learn MAC address to port mapping like a actual layer 2 switch. 
#### The difference between `digest` and `cpu` is that `disgest` packet contain only partial data to save resources while `cpu` packet uses the full packet. As we are currently only on the tutorial and are not as picky about resources, we will be using `cpu` solution. 
## Packet Tracer Topology
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/928fe757-d84d-44af-9c14-0e45b2d71a07)
## P4 Mininet
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/dc25f2ae-c8b9-4499-be5d-d845e47478b1)
## P4 Switch Thrift Port
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/203a1a9d-cc69-4413-accd-db980c195bf0)
## Flow Rules 
### Before ‘l2_learning_controller.py’ is executed. 
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/e840fa8e-81d7-4713-a62d-7ade11efb813)
### After ‘l2_learning_controller.py’ is executed. 
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/d7139d8b-688f-4d7e-9239-8a5e9800db4d)
### Before pingall command is sent
## ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/042d2de7-22c1-4fef-b166-8475c3f078cc)
### After pingall command is sent. 
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/c417abdf-592c-4d78-8425-96f407c5aa91)
#### The flow rules of the switch will first go through the smac table to find the source MAC address of the packet, then go through the dmac table to find the destination MAC address of the packet, and will apply the broadcast table if needed. 
## Flow Chart
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/62399df5-dc36-4e8e-a768-3bab6d8a514d)
### 1. Parser 
```
state start {
	packet.extract(hdr.ethernet);
	transition accept;
}
```
When the P4 switch receives a packet, its parser state will switch to start state and extract the ethernet header from the packet before transitioning to accept mode. 
### 2. Verify Checksum
`No action to be taken. `
### 3. Ingress Processing
```
action mac_learn() {
	meta.ingress_port = standard_metadata.ingress_port;
	clone3(CloneType.I2E, 100, meta);
}
```
This action section set the meta field of the packet metadata structure to the ingress port. It then clones the packet using the `clone3()` function with the following parameter, `CloneType.I2E` which meant ingress to egress cloning, `100` which meant clone session id of 100, `meta` which meant based on the captured metadata, to learn the ingress port value. 
```
table smac {
	key = {
		hdr.ethernet.srcAddr: exact;
	}
	actions = {
		mac_learn;
		NoAction;
	}
	size = 256;
	default_action = mac_learn;
}
```
Table smac is defined with a single key field, `hdr.ethernet.srcAddr`, which represents the source MAC address of the packet headers being process. The line `hdr.ethernet.srcAddr: exact;` meant that the key field is to be matched exactly. The `actions` section defines two action that can be taken, `mac_learn` which was declared above and `NoAction` which by default meant no action to be taken. The table size is set to hold up to 256 entries using `size = 256`. 
```
action forward(bit<9> egress_port) {
	standard_metadata.egress_spec = egress_port;
}
```
This `forward` action section set the output port for the packet as the egress port parameter of the P4 switch. While the `broadcast` action section has no action but will act as a trigger for another table for the flow rule. 
```
table dmac {
	key = {
		hdr.ethernet.dstAddr: exact;
	}
	actions = {
		forward;
		NoAction;
	}
	size = 256;
	default_action = NoAction;
}
```
Table dmac is defined with a single key field, `hdr.ethernet.dstAddr`, which represents the destination MAC address of the packet headers being process. The line `hdr.ethernet.dstAddr: exact;` meant that the key field is to be matched exactly. The `actions` section defines two actions that can be taken, `forward` which was declared above and `NoAction` which by default meant no action to be taken. The table size is set to hold up to 256 entries using `size = 256`. 
```
action set_mcast_grp(bit<16> mcast_grp) {
	standard_metadata.mcast_grp = mcast_grp;
}
```
This `set_mcast_grp` action section set the multicast group identifier for the egress packet. 
```
table broadcast {
	key = {
		standard_metadata.ingress_port: exact;
	}
	actions = {
		set_mcast_grp;
		NoAction;
	}
	size = 256;
	default_action = NoAction;
}
```
Table select_mcast_grp is defined with a single key field, `standard_metadata.ingress_port`, which represents the port where the processing packet was received from. The line `standard_metadata.ingress_port : exact;` meant that the key field is to be matched exactly. The `actions` section defines two actions that can be taken, `set_mcast_grp` which was declared above and `NoAction` which by default meant no action to be taken. The table size is set to hold up to 256 entries using `size = 256`. 
```
apply {
	smac.apply();
	if (dmac.apply().hit){
	}
	else {
		broadcast.apply();
} }
```
The apply block logic goes as follows, apply the `smac table` to learn the source MAC address, apply `dmac table` to learn destination MAC address, if unable to learn destination MAC address, apply `broadcast table`. 
### 4. Egress Processing
```
apply {
	if (standard_metadata.instance_type == 1){
		hdr.cpu.setValid();
		hdr.cpu.srcAddr = hdr.ethernet.srcAddr;
		hdr.cpu.ingress_port = (bit<16>)meta.ingress_port;
		hdr.ethernet.etherType = L2_LEARN_ETHER_TYPE;
		truncate((bit<32>)22); 
} }
```
The egress processing will check if the packet was cloned for learning by checking if its an ingress clone using `standard_metadata.instance_type == 1`. If it is, it then adds a CPU header data and sets the ethernet type to `L2_LEARN_ETHER_TYPE`, then truncates the packet to fit both the ethernet header and CPU header. 
### 5. Compute Checksum
`No action is taken. `
### 6. Deparser
```
apply {
	packet.emit(hdr.ethernet);
	packet.emit(hdr.cpu);
}
```
After extracting the ethernet header and CPU header to process, the P4 switch need to re-encapsulate the new processed header back to the packet before the packet egress. 
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
