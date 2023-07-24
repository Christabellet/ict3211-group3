![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/628c64e3-90aa-4cc6-9da6-c2eed601df66)﻿## Tutorial Link: https://github.com/nsg-ethz/p4-learning/tree/master/exercises/02-Repeater/thrift 
#### This tutorial main objectives is to make a switch act as a packet repeater between two hosts. 
## Packet Tracer Topology
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/72b263d6-457b-458e-b762-0342e09f9e4f)
## P4 Mininet
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/fa9a4825-769c-4514-a862-c3a763eca4b4)
## Flow Chart
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/b2b011a7-59ff-40d1-b886-484c7d3abfbf)
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
