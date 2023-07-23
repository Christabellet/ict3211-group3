# Tutorial Link: https://github.com/nsg-ethz/p4-learning/tree/master/exercises/02-Repeater/thrift 
#### This tutorial main objectives is to make a switch act as a packet repeater between two hosts. 
## Packet Tracer Topology
  
## P4 Mininet
  
## Flow Chart
  
### 1. Parser 
```
state start {
	transition accept;
}
```
When the P4 switch receives a packet, its parser state will start transitioning to accept mode. 
### 2. Verify Checksum
```No action is taken. ```
### 3. Ingress Processing
```
if (standard_metadata.ingress_port == 1){
	standard_metadata.egress_spec = 2;
}
else if (standard_metadata.ingress_port == 2){
	standard_metadata.egress_spec = 1;
}
```
By default, all packets will be dropped if there is no configuration in the ingress. In this case, the ingress will check if the receiving port is from port 1 or port 2 and set the egress port of the standard metadata to either port 2 or port 1 respectively, else it will be dropped as per default. 
### 4. Egress Processing
```No action is taken. ```
### 5. Compute Checksum
```No action is taken. ```
### 6. Deparser
``` No action is taken, as there is no specific header to deparse. ```
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