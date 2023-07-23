# Tutorial Link: https://github.com/nsg-ethz/p4-learning/tree/master/exercises/03-L2_Basic_forwarding/thrift
#### This tutorial main objective is to implement a basic layer 2 forwarding switch. However, note that it uses static mapping of MAC addresses to port, as such, it's behaviour does not match a real life switch.  
## Packet Tracer Topology
  
## P4 Mininet
  
## Flow Rules 
  
  
### 1. Dumping entry
``` The dumping entry shows the sequence of the packet information that is processed in the P4 switch. ```
### 2. Match key
``` The match key specifies the criteria for matching the packet against the entry, which in this screenshot entry ‘0x0’ shows the match key is ‘ethernet.dstAddr’ with exact match of ‘00000a000001’. ```
### 3. Action entry
``` The action entry specifies the action to be taken whether the packet has matches or not given the entry. The entry ‘0x0’ action shows ‘MyIngress.forward - 01’. ```
### 4. Dumping default
```The dumping default will occur when there is no specific match found in the table, in this screenshot, it shows ‘NoAction’ which means that no action will be taken. ```
## Flow Chart
  
### 1. Parser
```
state start {
            packet.extract(hdr.ethernet);
            transition accept;
        }
```
When the P4 switch receives a packet, its parser state will start transitioning to accept mode. 
### 2. Verify Checksum
```No action is taken. ```
### 3. Ingress Processing
```
action forward(bit<9> egress_port) {
            standard_metadata.egress_spec = egress_port;
        }
```
This ‘forward’ action section set the output port for the packet as the egress port parameter of the P4 switch. 
```
table dmac {
	key = {
		hdr.ethernet.dstAddr: exact;
}
	actions = {
		Forward;
		NoAction;
	}
	size = 256;
	default_action = NoAction;
	}
```
Table dmac is defined with a single key field, ```hdr.ethernet.dstAddr```, which represents the destination MAC address of the packet headers being process. The line ```hdr.ethernet.dstAddr: exact;``` meant that the key field is to be matched exactly. The ```actions``` section defines two actions that can be taken, ```forward``` which was declared above and ```NoAction``` which by default meant no action to be taken. The table size is set to hold up to 256 entries using ```size = 256```. 
```
apply {
	dmac.apply();
    }
```
The ```apply``` block invokes the table dmac using ```dmac.apply()``` statement. This is similar to calling a function in the main block, where the function is table dmac. 
### 4. Egress Processing
```No action is taken. ```
### 5. Compute Checksum
```No action is taken. ```
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