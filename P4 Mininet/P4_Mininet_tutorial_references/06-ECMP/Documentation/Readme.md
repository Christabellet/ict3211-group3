## Explanation of the code
#### The objective of this exercise is to implement a layer 3 forwarding switch that is able to load balance traffic towards a destination across equal cost paths. 

In this exercise, you will require these files.
| File | Description |
| --- | --- |
| `p4app.json` | creates the topology of the network diagram |
| `headers.p4` | defines the headers of the p4 code |
| `parsers.p4` | defines the parsers of the p4 code |
| `ecmp.p4` | p4 program that defines how packets should flow in a network diagram |
| `s1-commands.txt` | forwarding entries to tables

In the header.p4 file, it contains the headers and the metadata defined in the file. 

In the parser.p4 file, it extracts the headers from the incoming packets and organize them into their corresponding data struc

### 1. Parser
```
parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) 
```
The parser block `MyParser` takes in 4 parameters `packet_in packet`, `out headers hdr`, `inout metadata meta`, and `inout standard_metadata_t standard_metadata`.
```
    state start {
        transition parse_ethernet;
    }
```
This defines the initial start state of the parser. The command `transition parse_ethernet` moves the parser to the next state `parse_ethernet` to extract the Ethernet header from the packet.
```
    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType){
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }
```
In this state `parse_ethernet`, it extracts the Ethernet header from the packet and stores it in the `hdr.ethernet` defined in the header file. `transition select(hdr.ethernet.etherType)` the parser uses a `select` statement to check the `etherType` field in the Ethernet header. `TYPE_IPV4: parse_ipv4` checks if the Ethernet type is `TYPE_IPV4`, if yes then it transits into `parse_ipv4` state to extract the IPv4 header from the packet. `default: accept` defines that if the protocol is not IPv4, the parser will just accept the packet without parsing further. 
```
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol){
            6 : parse_tcp;
            default: accept;
        }
    }
```
In this state `parse_ipv4`, it extracts the IPv4 header from the packet and stores it in the `hdr.ipv4.transition select(hdr.ipv4.protocol)` the parser uses a `select` statement to check the `protocol` field of the IPv4 header. `6 : parse_tcp` checks that if the protocol is `6` which represents TCP. The parser transits to  `parse_tcp` to extract the TCP header from the packet. `default: accept` defines that if the protocol is not TCP, the parser will just accept the packet without parsing further. 
```
    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }
}
```
In this `state parse_tcp` , it extracts the TCP header from the packet and stores them in the `hdr.tcp`. After successfully parsing the TCP header, the parser accepts the packet indicating that the parsing process is complete. 

### 2. Ingress Processing
```
control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
```
The control block takes in 3 parameters `inout headers hdr`, `inout metadata meta` and `inout standard_metadata_t standard_metadata`. 

There are 3 actions defined in this process.
```
    action drop() {
        mark_to_drop(standard_metadata);
    }
```
This action `drop()` is called when the control logic decides to drop the packet. It calls the `mark_to_drop` function which passes in the `standard_metadata` as an argument. 
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
This action `ecmp_group(bit<14> ecmp_group_id, bit<16> num_nhops)` which computes a hash value `meta.ecmp_hash` using the CRC16 hash algorithm based on the source IP, destination IP, source port, destination port and IP protocol fields. The `num_nhops` argument specifies the number of next hops for the ECMP group. `meta.ecmp_group_id = ecmp_group_id` would set the `meta.ecmp_group_id `to `Ecmp_group_id`. 
```
action set_nhop(macAddr_t dstAddr, egressSpec_t port) {
        //set the src mac address as the previous dst, this is not correct right?
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
       //set the destination mac address that we got from the match in the table
        hdr.ethernet.dstAddr = dstAddr;
        //set the output port that we also get from the table
        standard_metadata.egress_spec = port;
        //decrease ttl by 1
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }
```
This action `set_nhop` sets the next-hop information for the packet. It sets the destination MAC address to `dstAddr`, sets the output port `standard_metadata.egress_spec` to `port`. It also decrement the `hdr.ipv4.ttl` field in the IPv4 header. 
```
    table ecmp_group_to_nhop {
        key = {
            meta.ecmp_group_id:    exact;
            meta.ecmp_hash: exact;
        }
        actions = {
            drop;
            set_nhop;
        }
        size = 1024;
    }
```
This table `ecmp_group_to_nhop` uses meta.`ecmp_group_id` and meta.`ecmp_hash` as keys to perform a lookup. Both keys match are defined as exact. 

There are 2 possible actions defined in this table.
`drop`: If there are no matching entries found, the packet would be dropped.
`set_nhop`: If there are matching entries found, it will perform the `set_nhop` action.

The `size` parameter defines the maximum number of entries the table can hold. In this example, the table has a size of 1024.
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
This table `ipv4_lpm` is used to perform a destination-based forwarding. It uses `hdr.ipv4.dstAddr` as the key and `lpm` defines the attribute that the lookup will be performed using the longest prefix match algorithm. 

There are 3 possible actions defined in this table. 
`set_nhop`: If there are matching entries found, one possible action that it will perform is the set_nhop action.
`ecmp_group`: Ifgro there are matching entries found, another possible action that it will perform is the ecmp_up action.
`drop`: If there are no matching entries found, by default the packet would be dropped.

The `size` parameter defines the maximum number of entries the table can hold. In this example, the table has a size of 1024.

In this example, each switch has its own text file configurations for their forwarding. As an example, we will use `s1-commands.txt`.
```
table_set_default ipv4_lpm drop
table_set_default ecmp_group_to_nhop drop
```
This command `table_set_default` sets both table `ipv4_lpm` and `ecmp_group_to_nhop` default action to `drop`
```
table_add ipv4_lpm set_nhop 10.0.1.1/32 =>  00:00:0a:00:01:01 1
```
This command adds an entry to the `ipv4_lpm` table. If the packets matches the destination of `10.0.1.1/32`, it would execute the `set_nhop`  action, which sets the destination MAC address to  `00:00:0a:00:01:01` and egress port to `1`
```
table_add ipv4_lpm ecmp_group 10.0.6.2/32 => 1 4
```
This command adds an entry to the `ipv4_lpm` table. If the packet matches the destination of `10.0.6.2/32`, it would execute the `ecmp_group` action, which computes the ECMP group with `ecmp_group_id` equals to 1 and `num_nhops` to  `4`.
```
//ecmp id:1 port 0,1,2,3
table_add ecmp_group_to_nhop set_nhop 1 0 =>  00:00:00:02:01:00 2
table_add ecmp_group_to_nhop set_nhop 1 1 =>  00:00:00:03:01:00 3
table_add ecmp_group_to_nhop set_nhop 1 2 =>  00:00:00:04:01:00 4
table_add ecmp_group_to_nhop set_nhop 1 3 =>  00:00:00:05:01:00 5
```
This command adds entries into the `ecmp_group_to_nhop` table. For example, `table_add ecmp_group_to_nhop set_nhop 1 0 =>  00:00:00:02:01:00 2`
If the packets with a match of  `ecmp_group_id` equals to 1 and `num_nhops` equals to 0, `set_nhop` will be executed. It will set the destination MAC address to `00:00:00:02:01:00` and the egress port to `2`.
```
    apply {
        if (hdr.ipv4.isValid()){
            switch (ipv4_lpm.apply().action_run){
                ecmp_group: {
                    ecmp_group_to_nhop.apply();
                }
            }
        }
    }
}
```
The apply block is responsible for processing the incoming packets and making the forwarding decisions based on the routing logic. The if statement `hdr.ipv4.isValid()` would check if the IPv4 header in the incoming back is valid. If the condition is true, `ipv4_lpm.apply().action_run` where it performs a lookup in the `ipv4_lpm` table based on the destination address. The switch statement is used to handle the different results from the lookup in the ipv4_lpm table. If the results belongs to `ecmp_group`, it will apply the `ecmp_group_to_nhop` action which determines the specific next-hop for packets belonging to ECMP group.

### 3. Checksum Compuation 
```
control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
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
              hdr.ipv4.dstAddr },
              hdr.ipv4.hdrChecksum,
              HashAlgorithm.csum16);
    }
}
```
The control block `MyComputeChecksum` ensures that the checksum is calculated correctly for the valid IPv4 packets before it is forwarded. 
