## Explanation of the code
#### The objective of this exercise is to create a basic topology with host and p4 switches along with adding links connecting them together. Implementing a p4 program to enable switches to bounce back packets to the interface that they came from.

In this exercise, you would require 3 files as shown below, 

| File | Description |
| --- | --- |
| `p4app.json` | creates the topology of the network diagram |
| `reflector.p4` | p4 program that defines how packets should flow in a network diagram |
| `send_receive.py` | python script to send and receive packets|

In the reflector.p4 file, there are 7 sections which are the headers, parser, checksum verification, ingress processing, egress processing, checksum computation, deparser

### 1. Header
It is used to define the necessary headers and structures used in the packet processing pipeline. 
```
typedef bit<48> macAddr_t;
```
This command is a declaration that defines a new data type called `macAddr_t` and is represented as a bit-vector of length 48.
```
header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}
```
The `ethernet_t` creates data structure to represent Ethernet frames. It consists of 3 fields `dstAddr` which stores the destination MAC address, `srcAddr` which stores the source MAC address and `etherType` which is used to indicate the type of payload encapsulated in the Ethernet frame.
### 2. Parser 
It is used to extract headers from the incoming packet and convert it into a structured format. 
```
parser MyParser(packet_in packet,
               out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata)
```
`MyParser` is the parser block which takes in 4 parameters:
`packet_in packet`:Incoming packets that the parser will process
`out headers hdr`: Structure where the parser will store the extracted headers from the incoming packets
`inout metadata meta`:Optional metadata structure that can be used to store additional information about the packet during parsing 
`inout standard_metadata_t standard_metadata`:standard_metadata structure that contains various fields related to packet processing, such as ingress port, egress port, ingress timestamp
```
 state start{
  	  packet.extract(hdr.ethernet);
          transition accept;
      }
```
This defines the starting state of the parser.
```
packet.extract(hdr.ethernet)
```
This command would extract the `ethernet` from the incoming packet and store it in the `hdr`. Since the `ethernet_t` was defined in the header section with fields `dstAddr`,`srcAddr` and `etherType`. For example, the destination MAC address from the packet will be stored in the ‘hdr.ethernet.dstAddr’ etc. 
```
transition accept
```
This command indicates that the parsing process is complete and it will transit into the ‘accept’ state. 

### 3. Checksum Verification, 
It handles the verification of the checksums in the packet header. 
```
control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}
```
The control block `MyVerifyChecksum` takes in 2 parameters `inout headers hdr` and `inout metadata meta`. 
The `apply {  }` is currently empty as there is no specific checksum verification logic implemented. 

### 4. Ingress Processing
it is responsible for processing the incoming packets after they are parsed. 
```
control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

```
The control block `MyIngress` takes in 3 parameters inout headers `hdr`, `inout metadata meta` and `inout standard_metadata_t standard_metadata`. 
```
swap_mac() 
```
This command is used to swap the source MAC address and the destination MAC address in the ‘ethernet’ header of the packet. 
```
macAddr_t tmp;
tmp = hdr.ethernet.srcAddr;
	   hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
	   hdr.ethernet.dstAddr = tmp;
```
`tmp` is a temporary variable which is used to store the source MAC address. Then the source MAC address would be replaced by the destination MAC address. Lastly, the destination MAC address would then be written as the value of `tmp` which was used to store the original source MAC address. This is how the swapping of MAC addresses takes place. 
```
    apply {
       // Swap MAC addresses.
       swap_mac();
```
The apply block is where the actions are being processed. Hence, by calling the `swap_mac()` action, it executes the processes. 
```
 standard_metadata.egress_spec = standard_metadata.ingress_port;
```
This command is used to set the value of the egress_spec which represents the output port to which the packet will be forwarded to the value of the ingress_port which represents the number of ingress ports which the packet received. This would ensure that the packet is sent back through the same port as it was received. 

### 5. Deparser
It is responsible for the converting of processed packets back into its raw form before transmission. 
```
control MyDeparser(packet_out packet, in headers hdr) {
    apply {
		// parsed headers have to be added again into the packet
		packet.emit(hdr.ethernet);
	}
}
```
The control block `MyDeparser` takes in 2 parameters `packet_out packet` which represents the packet that will be deparsed and prepared for transmission and `in headers hdr` which represents the structured header information that was updated during the packet processing stages. 
```
packet.emit(hdr.ethernet)
```
This command would convert the `hdr.ethernet` which is defined previously in the `header ethernet_t` into their binary representation. These fields would append to the end of the outgoing packet. After emitting the header, the packet will now contain the entire raw binary representation of the outgoing packet. Once deparsing is completed, the packet will be ready to be sent out through the network interface to its intended destination. 






