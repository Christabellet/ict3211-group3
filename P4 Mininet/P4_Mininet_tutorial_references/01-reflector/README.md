## Tutorial Link: https://github.com/nsg-ethz/p4-learning/tree/master/exercises/01-Reflector 
#### This tutorial main objective is to show us how to create a simple topology in P4 Mininet, then make the switch simple bounce back packets to the receiving interface. 
## Packet Tracer Topology
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/6334d459-a1ff-41f1-807a-dc8303171711)
## P4 Mininet
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/a2ef7368-3ce2-498d-8214-20d7d55198de)
## Flow Chart
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/65fc1caf-c43f-4e5c-ac7a-e2bd5f55cfc2)
### 1. Parser 
```
state start{
	packet.extract(hdr.ethernet);
	transition accept;
}
```
When the P4 switch receives a packet, its parser state will switch to start state and extract the ethernet header from the packet before transitioning to accept mode. 
```
header ethernet_t {
	macAddr_t dstAddr;
	macAddr_t srcAddr;
	bit<16>   etherType;
}
```
This is the ethernet header structure that is declared to be inside the packet. 
### 2. Verify Checksum
```No action is taken. ```
### 3. Ingress Processing
```
action swap_mac(){
   macAddr_t tmp;
   tmp = hdr.ethernet.srcAddr;
   hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
   hdr.ethernet.dstAddr = tmp;
}
```
To swap the source and destination mac address, an action table is required to put it into motion. An action table is similar to an function in common programming language, to call the function, apply will be needed as seen in the next mark down. 
```
apply {
   swap_mac();
   standard_metadata.egress_spec = standard_metadata.ingress_port;
}

```
This markdown also includes setting the egress port as the ingress port, to reflect the packet back to the same port. 
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
