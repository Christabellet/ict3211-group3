## Tutorial Link: https://github.com/nsg-ethz/p4-learning/tree/master/exercises/05-ECMP
#### This tutorial main objective is to implement a layer 3 load balancing traffic across multiple equal cost path. 
## Packet Tracer Topology
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/e8363d25-57b7-4144-9d77-467bb574bd64)
## P4 Mininet
#### ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/aac13c64-eb45-4ada-88e9-d2831c9f39a1)
#### Here we can see that the ping request and reply for h1 and h2 took a different path upon closer inspection on the timing of the packet. However, it does not look like a load balancing has occurred as there is no congestion. We can do another test to see a better visual look at ECMP load balancing. 
#### ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/6d70e124-f668-434f-89fd-71d4f9c63b1f)
#### Here by simply sending slightly more packets, we are able to simulate the ECMP load balancing. 
## P4 Switch Thrift Port
#### ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/f3098615-dd86-421a-89d2-b4d5dba00594)
#### The P4 switch thrift port allows the user to use CLI to access the P4 switch.
## Flow Rules
#### This is the flow rules of the S1:
#### ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/8596437d-b875-4924-99dd-f37288c25e9a)
#### The P4 switch flow rules will first go through ipv4_lpm table including forwarding to the next hop, forwarding to an ECMP group, or dropping the packet. 
#### If the flow rules dictate that the ecmp_group_to_nhop is used, it will determine the next hop for the packet that belongs to a specific ECMP group, `scalars.userMetadata.ecmp_group_id`, based on their calculated hash values, `scalars.userMetadata.ecmp_hash`. The table will map both the ECMP group identifier and hash value to the specific next hop identifier, in this way, it allows the switch to perform some sort of load balancing across multiple paths with equal cost. 
#### This is the flow rules of S2:
#### ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/230132d6-13bf-4b45-af59-6a80b813840f)
#### There is no entry for the ecmp_group_to_nhop table as the P4 switch does not need to take ECMP into consideration since it only has a ingress and a egress port. 
#### This is the flow rules of S3: 
#### ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/54137788-1bbf-4576-8f24-50e7928eedec)
#### This is the flow rules of S4:
#### ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/92a5eafb-5fa3-428b-a65b-0f2d6e847c6a)
#### This is the flow rules of S5:
#### ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/11ab50ea-7b36-46aa-b19a-d6f12f854a81)
#### This is the flow rules of S6:
#### ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/3a9bdd5f-8806-4cbc-aac2-8f05985fa783)
## Possible packet path
#### ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/3cfa182c-a9d1-4a80-942c-c1583270c3d3)
#### This is a simple possible path that the packet can take when there is a meagre amount of traffic. 
#### ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/842119c9-2ad8-4712-837f-a0e0d15892bc)
#### This is also another possible path that the packet can take when there are higher amount of traffic, the return path can differ from the sending path to load balance the network traffic. It is similar to this for the other three sending pathways such as 
1. H1->S1->S3->S6->H2->S6->S2->S1->H1
2. H1->S1->S3->S6->H2->S6->S4->S1->H1
3. H1->S1->S3->S6->H2->S6->S5->S1->H1
4. H1->S1->S4->S6->H2->S6->S2->S1->H1
5. H1->S1->S4->S6->H2->S6->S3->S1->H1
6. H1->S1->S4->S6->H2->S6->S5->S1->H1
7. H1->S1->S5->S6->H2->S6->S2->S1->H1
8. H1->S1->S5->S6->H2->S6->S3->S1->H1
9. H1->S1->S5->S6->H2->S6->S4->S1->H1
#### Read the flow chart below with its description to understand further what the packet process is like during the packet travel in the P4 switch. 
## Flow Chart
# ![image](https://github.com/PototoPatata/ict3211-group3/assets/20123754/e12eb5a9-18e2-4e6b-b287-01531f6ec9cc)
### 1. Parser
```
state start {
	transition parse_ethernet;
}
```
When P4 switch receive a packet, its parser state will switch to start state and transition to `parse_ethernet` mode.
```
state parse_ethernet {
	packet.extract(hdr.ethernet);
	transition select(hdr.ethernet.etherType){
		TYPE_IPV4: parse_ipv4;
		default: accept;
} }
```
In the `parse_ethernet`, `packet.extract(hdr.ethernet)` will extract the ethernet header. `transition select()` will determine the next state, in this case by checking the value of `hdr.ethernet.etherType`. If the value of `hdr.ethernet.etherType` is `TYPE_IPV4` or 0x800 which represents the ethernet frame that encapsulates an IPv4 packet, the parser state will transition to `parse_ipv4` state, else it will default to `accept` state. 
```
state parse_ipv4 {
	packet.extract(hdr.ipv4);
	transition select(hdr.ipv4.protocol){
		6 : parse_tcp;
		default: accept;
} }
```
In the `parse_ipv4` state, `packet.extract(hdr.ipv4)` will extract the IPv4 header. `transition select()` will determine the next state, in this case by checking the value of `hdr.ipv4.protocol`. If the value of `hdr.ipv4.protocol` is `6`, the protocol number for TCP in IP protocol field, which means the IP packet encapsulates a TCP segment, the parser state will transition to `parse_tcp` state, else it will default to `accept` state. 
```
state parse_tcp {
	packet.extract(hdr.tcp);
	transition accept;
}
```
In the `parse_tcp` state, `packet.extract(hdr.tcp)` will extract the TCP header and transition to accept mode. 
### 2. Verify Checksum
`No action is taken. `
### 3. Ingress Processing
```
action ecmp_group(bit<14> ecmp_group_id, bit<16> num_nhops){
	hash(meta.ecmp_hash,
	HashAlgorithm.crc16,
	(bit<1>)0,
	{ hdr.ipv4.srcAddr,
	  hdr.ipv4.dstAddr,
	  hdr.tcp.srcPort,
	  hdr.tcp.dstPort,
	  hdr.ipv4.protocol},
	num_nhops);
	meta.ecmp_group_id = ecmp_group_id;
}
```
This action section takes in two parameter, `ecmp_group_id` which is the ECMP group identifier and `num_nhops` which is the number of next hops. The hash function is for calculating the hash value, which the hash algorithm will use `HashAlgorithm.cr16` and the result of the hash value will be stored in `meta.ecmp_hash`. The list of fields from the packet headers are the fields over which the hash will be calculated and the ECMP group ID will be stored in the metadata. 
```
action set_nhop(macAddr_t dstAddr, egressSpec_t port) {
	hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
	hdr.ethernet.dstAddr = dstAddr;
	standard_metadata.egress_spec = port;
	hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
}
```
This action section updates the ethernet source and destination address, setting the egress port, and decreasing the IPv4 time-to-live field by one. 
```
table ecmp_group_to_nhop {
	key = {
		meta.ecmp_group_id: exact;
		meta.ecmp_hash: exact;
	}
	actions = {
		drop;
		set_nhop;
	}
	size = 1024;
}
```
Table ecmp_group_to_nhop is defined with two key field, `meta.ecmp_group_id` and `meta.ecmp_hash`, which will represent the ECMP group identifier and hash value in the metadata of the packet respectively. Being tagged with `exact` meant that actions will be taken when the field are being matched exactly, the action `set_nhop` is mentioned above. The table size is set to hold up to 1024 entries using `size = 1024`. 
```
table ipv4_lpm {
	key = {
		hdr.ipv4.dstAddr: lpm;
	}
	actions = {
		set_nhop;
		ecmp_group;
		drop;
	}
	size = 1024;
	default_action = drop;
}
```
Table ipv4_lpm is defined with a single key field, `hdr.ipv4.dstAddr`, which will represent the destination address IPv4 header. Being tagged with `lpm` meant the switch will attempt to match the destination IP address against the prefix in the routing table based on the longest prefix, the action `set_nhop` and `ecmp_group` is mentioned above. The table size is set to hold up to 1024 entries using `size = 1024`. 
```
apply {
	if (hdr.ipv4.isValid()){
		switch (ipv4_lpm.apply().action_run){
			ecmp_group: {
				ecmp_group_to_nhop.apply();
	} } } }
```
The apply block logic goes as follows, `if (hdr.ipv4.isValid())` check if IPv4 header in the packet is valid, `switch (ipv4_lpm.apply().action_run)` apply the `ipv4_lpm` table if valid, `ecmp_group` check if `.action_run` matches itself, if yes, run `ecmp_group_to_nhop.apply()` which is for the load balancing across multiple path that are equal in cost. 
### 4. Egress Processing
`No action is taken. `
### 5. Compute Checksum
```
Update_checksum
```
This first argument is a boolean that decide if the `MyComputeChecksum` function needs to be updated or not. In this case, `hdr.ipv4.isValid()` is used, which by default is already verified during the ingress processing. 
```
{ hdr.ipv4.version,
	hdr.ipv4.ihl,
	hdr.ipv4.dscp,
	hdr.ipv4.ecn,
	hdr.ipv4.totalLen,
	hdr.ipv4.identification,
	hdr.ipv4.flags,
	hdr.ipv4.fragOffset,
	hdr.ipv4.ttl,
	hdr.ipv4.protocol,
	hdr.ipv4.srcAddr,
	hdr.ipv4.dstAddr }
```
These are the list of fields which the checksum is to be calculated using `HashAlgorithm.csum16` over several fields of the IPv4 header. 
```
hdr.ipv4.hdrChecksum
```
This argument is where the calculated checksum will be stored. 
### 6. Deparser
```
apply {
	packet.emit(hdr.ethernet);
	packet.emit(hdr.ipv4);
	packet.emit(hdr.tcp);
}
```
After extracting the ethernet header and IPv4 header to process, the P4 switch needs to re-encapsulate the new processed header back to the packet before the packet egress. As there might be some packets that process the TCP header as well, the P4 switch will check if it needs to re-encapsulate it. 
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
