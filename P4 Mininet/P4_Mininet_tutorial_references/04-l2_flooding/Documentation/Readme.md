## Explanation of the code
#### The objective of this exercise is to implement layer 2 flooding. In this case, when a layer 2 switch does not know which port to forward the packets to, the switch will send the packet to all the ports but not the port that the packet came from. 

In this exercise, you would require 3 files as shown below, 
| File | Description |
| --- | --- |
| `p4app.json` | creates the topology of the network diagram |
| `l2_flooding_other_ports.p4` | p4 program that defines how packets should flow in a network diagram |
| `s1-commands.txt` | forwarding entries to table |

Under the l2_flooding_other_ports.p4 file, 

In the beginning of the code, there are 2 constants that are being defined. 
```
const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_BROADCAST = 0x1234;
```
The first command defines a constant named `TYPE_IPV4`. `0x800` is the EtherType which represents IPv4 packets. EtherType is a field in the Ethernet header that identifies the payload protocol. When there is an incoming packet, the switch can use this constant to check if the Ethernet type of the packet matches the value `0x800` which indicates that it is an IPv4 packet. 
The second command defines another constant named `TYPE_BROADCAST` and has a value of `0x1234` which is 4660 in decimal. This constant represents a custom Ethernet type used to identify broadcast packets. 

### 1. Header
```
typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
```
They are the egress port with a bit-width of 9 bits, MAC address with a bit-width of 48 bits and ipv4 address with a bit-width of 32 bits. 
```
header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}
```
The header block `ethernet_t`, it declares the field `dstAddr` and `srcAddr` which represents the destination MAC address and source MAC address of the Ethernet frame. It also declares a field `etherType`. It is used to indicate the payload encapsulated in the Ethernet frame. For example, 0x800 represents IPv4 payload. 
```
struct headers {
    ethernet_t   ethernet;
}
```
The struct block `headers` is defined to encapsulate header instances used in packet processing. It is used as a container to group multiple header instances together. The line `ethernet_t ehernet` declares a field named `ethernet` inside the struct using the previously defined `ethernet_t` header. By encapsulating headers within the struct, it makes it easier to pass the header as a single unit rather than multiple headers. 

### 2. Parser
It is used to extract any headers from the incoming packets. 
```
parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) 
```
The parser block `MyParser` takes in 4 parameters `packet_in packet`, `out headers hdr`, `inout metadata meta`, and `inout standard_metadata_t `
```
    state start {
        packet.extract(hdr.ethernet);
        transition accept;
    }
```
This defines the initial state of the parser. The line `packet.extract(hdr.ethernet)` extracts the `ethernet_t` header from the incoming packet and stores it in the `hdr.ethernet` variable. When a packet is received, the parsing process would start and parse the raw packet data and populate the fields of the `hdr.ethernet` with the corresponding values from the packet. The line `transition accept` specifies that the parsing process is completed and transited to the accept state which allows further processing of the packets.

### 3. Ingress Processing
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
    action forward(bit<9> egress_port) {
        standard_metadata.egress_spec = egress_port;
    }
```
This action `forward(bit<9> egress_port)` is called when the control logic decides to forward the packet. It takes in a 9 bit argument, `egress_port`.  It sets the `standard_metadata.egress_spec` to the specified `egress_port`. 
```
    action broadcast() {
        //Empty action that was not necessary, we just call it when there is a table miss
    }
```
This action `broadcast()` is empty and does not perform any actions. It is used as a placeholder and is only called when there is no matching entry found in the `dmac` table.
```
    table dmac {
        key = {
            hdr.ethernet.dstAddr: exact;
        }
```
This table `dmac` is used to perform destination MAC address based forwarding. 
```
header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}
```
It uses the `hdr.ethernet.dstAddr` from the Ethernet header as the key, and the match type is defined as `exact`. 

There are 3 possible actions to be taken.
```
        actions = {
            forward;
            broadcast;
            NoAction;
        }
        size = 256;
        default_action = NoAction;
    }
```
`Forward`: If there is a matching entry in the table, this action will be applied.
`Broadcast`: This action is used to handle broadcast packets. It does not perform any forwarding action based on the Ingress Processing `broadcast()` action being empty. 
`NoAction`: If there is no matching entry in the table, this action will be default which indicates no forwarding is done. 

The `size` parameter defines the maximum number of entries the table can hold. In this example, the table has a size of 256. 

These entries will be stored in the `s1-commands-other-ports.txt`. 
```
table_add dmac forward 00:00:0a:00:00:01 => 1
table_add dmac forward 00:00:0a:00:00:02 => 2
table_add dmac forward 00:00:0a:00:00:03 => 3
table_add dmac forward 00:00:0a:00:00:04 => 4
table_set_default dmac broadcast
```
Each `table_add` command specifies a MAC address and the corresponding egress port to which that MAC address should be forwarded. 

For example, `table_add dmac forward 00:00:0a:00:00:01 => `1
This command adds an entry to the `dmac` table. The destination MAC address would be `00:00:0a:00:00:01`. The action associated with it is `forward`. The egress port that the forward action will forward the packet to is port of value `1`.
```
    action set_mcast_grp(bit<16> mcast_grp) {
        standard_metadata.mcast_grp = mcast_grp;
    }
```
The action block `set_mcast_grp` which takes in a parameter `mcast_grp` which is a 16 bit value representing the multicast group identifier. The command sets the value of the multicast group identifier for the packet. 
```
  table select_mcast_grp {
        key = {
            standard_metadata.ingress_port : exact;
        }
```
This table `select_mcast_grp` is used to map each ingress port to a multicast group identifier.  It uses the `standard_metadata.ingress_port` as the key, and the match type is defined as `exact`.
```
        actions = {
            set_mcast_grp;
            NoAction;
        }
        size = 32;
        default_action =  NoAction;
    }
```
There are 2 possible actions to be taken.
`set_mcast_grp`: Once a matching entry is found, this action will be executed.
`NoAction`: If there is no matching entry, by default there would be no action taken. 

The `size` parameter defines the maximum number of entries the table can hold. In this example, the table has a size of 32. 

These entries will be stored in the `s1-commands-other-ports.txt`. 
```
#define broadcasting port groups
mc_node_create 0 2 3 4
mc_node_create 1 1 3 4
mc_node_create 2 1 2 4
mc_node_create 3 1 2 3
```
Each `mc_node_create` specifies a multicast group and the egress port associated with that multicast group. For example, the first line `mc_node_create 0 2 3 4` creates a multicast node 0 with egress ports 2, 3 and 4 associated to it. 
```
#associate node group with mcast group
mc_mgrp_create 1
mc_node_associate 1 0

mc_mgrp_create 2
mc_node_associate 2 1

mc_mgrp_create 3
mc_node_associate 3 2

mc_mgrp_create 4
mc_node_associate 4 3
```
Each `mc_mgrp_create` creates a multicast group with a specific identifier. For example, the first line `mc_mgrp_create 1` creates a multicast group with identifier 1. Each `mc_node_associate` associates a multicast group with an identifier. For example, the second line `mc_node_associate 1 0` would associate multicast node 0 which is created above with the multicast group with identifier 1. 
```
#fill table selector
table_add select_mcast_grp set_mcast_grp 1 => 1
table_add select_mcast_grp set_mcast_grp 2 => 2
table_add select_mcast_grp set_mcast_grp 3 => 3
table_add select_mcast_grp set_mcast_grp 4 => 4
```
Each `table_add` fills the `select_mcast_grp` table with the rules that determine the multicast group identifier associated with each ingress port. 

For example, `table_add select_mcast_grp set_mcast_grp 1 => 1`
This command would add an entry to the `select_mcast_grp` table and map the `set_mcast_grp 1` which is the multicast group identifier of 1 to ingress port 1.
```
    apply {
        switch (dmac.apply().action_run) {
            broadcast: {
                select_mcast_grp.apply();
            }
```
This command would apply the logic implemented in the `dmac` for processing. When the packet arrives at the `dmac` table, it would determine whether the packet is unicast forwarded or broadcast. If the packet is labelled as broadcast, it would proceed to the `broadcast` block and apply the `select_mcast_grp table` to determine the multicast group identifier associated with the ingress port. The multicast group identifier would be used during egress processing to perform multicast forwarding to ensure that the packet is forwarded to all the egress ports associated. 
