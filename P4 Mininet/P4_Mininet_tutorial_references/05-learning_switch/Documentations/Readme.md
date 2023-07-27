## Explanation of the code
#### The objective of this exercise is to implement layer 2 learning. Rather than manually adding the MAC address to the egress port, in this exercise we would let the switch automatically map the MAC address to the port. 

In this exercise, you would require 2 files as shown below, 
| File | Description |
| --- | --- |
| `p4app.json` | creates the topology of the network diagram |
| `l2_learning_copy_to_cpu.p4` | p4 program that defines how packets should flow in a network diagram |

Under the l2_learning_copy_to_cpu.p4 file, 

In the beginning of the code, there are 2 constants that are being defined. 
```
const bit<16> TYPE_IPV4 = 0x800;
const bit<16> L2_LEARN_ETHER_TYPE = 0x1234;
```
The first command defines a constant named `TYPE_IPV4`. `0x800` is the EtherType which represents IPv4 packets. EtherType is a field in the Ethernet header that identifies the payload protocol. When there is an incoming packet, the switch can use this constant to check if the Ethernet type of the packet matches the value `0x800` which indicates that it is an IPv4 packet. 
The second command defines another constant named `L2_LEARN_ETHER_TYPE` and has a value of `0x1234` which is 4660 in decimal. This constant represents a custom Ethernet type used to identify broadcast packets. 

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
header cpu_t {
    bit<48> srcAddr;
    bit<16> ingress_port;
}
```
The header `cpu_t` consists of 2 fields: `srcAddr` which represents the 48 bits source MAC address and `ingress_port` which represents the 16 bits ingress port. 
```
struct headers {
    ethernet_t   ethernet;
    cpu_t        cpu;
}
```
The struct block `headers` is defined to encapsulate header instances used in packet processing. It is used as a container to group multiple header instances together. The line `ethernet_t ethernet` declares a field named `ethernet` inside the struct using the previously defined `ethernet_t header`. The line `cpu_t cpu` declares an instance of the `cpu_t` header type.  By encapsulating headers within the struct, it makes it easier to pass the header as a single unit rather than multiple headers. 

### 2. Parser
It is used to extract any headers from the incoming packets.
```
parer MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata)
```
The parser block `MyParser` takes in 4 parameters `packet_in packet`, `out headers hdr`, `inout metadata meta`, and `inout standard_metadata_t standard_metadata`.
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

There are 2 actions defined in this process.
```
    action drop() {
        mark_to_drop(standard_metadata);
    }
```
This action `drop()` is called when the control logic decides to drop the packet. It calls the `mark_to_drop` function which passes in the `standard_metadata` as an argument. 
```
    action mac_learn() {
        meta.ingress_port = standard_metadata.ingress_port;
        clone3(CloneType.I2E, 100, meta);
    }
```
This action `mac_learn()` is called when a packet is received and its purpose is to learn the ingress port from the `standard_metadata` and record it in the `meta` structure. The command `meta.ingress_port = standard_metadata.ingress_port` assigns the value of `standard_metadata.ingress_port` to the `meta.ingress_port`. The command `clone3(CloneType.I2E, 100, meta)` is to perform packet cloning using clone3. `CloneType.I2E` indicates the type of clone operation to be performed where `I2E` represents “Ingress to Egress” clone. The value `100` is the clone ID session, which specifies the specific clone session to use. `Meta` refers to the metadata structure, being passed as the third argument to provide additional information about the cloned packet. 
```
    table smac {
        key = {
            hdr.ethernet.srcAddr: exact;
        }
```
This table `smac` is used to perform source MAC address based forwarding. 
```
header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}
```
It uses the `hdr.ethernet.srcAddr` from the Ethernet header as the key, and the match type is defined as `exact`. 
```
        actions = {
            mac_learn;
            NoAction;
        }
        size = 256;
        default_action = mac_learn;
```
There are 2 possible actions to be taken.
`mac_learn`: Once the table lookup matches a valid entry for the given source address, this action will be executed.
`NoAction`: If there is no matching entry, by default there would be no action taken. 

The `size` parameter defines the maximum number of entries the table can hold. In this example, the table has a size of 256.
```
     action forward(bit<9> egress_port) {
        standard_metadata.egress_spec = egress_port;
    }
```
This action `forward(bit<9> egress_port)` is called when the control logic decides to forward the packet. It takes in a 9 bit argument, `egress_port`.  It sets the `standard_metadata.egress_spec` to the specified `egress_port`.
```
    table dmac {
        key = {
            hdr.ethernet.dstAddr: exact;
        }
```
This table `dmac` is used to perform destination MAC address based forwarding. It uses the `hdr.ethernet.dstAddr` from the Ethernet header as the key, and the match type is defined as `exact`.
```
    action set_mcast_grp(bit<16> mcast_grp) {
        standard_metadata.mcast_grp = mcast_grp;
    }
```
This action `set_mcast_grp(bit<16> mcast_grp)` takes in a parameter mcast_grp which is the 16 bit value representing the multicast group ID. It sets the `mcast_grp` field in the metadata to the value of the `mcast_grp`.
```
    table broadcast {
        key = {
            standard_metadata.ingress_port: exact;
        }
```
This table `broadcast` is used to perform broadcast MAC address based forwarding. It uses the ingress port field in the standard metadata as the key and the match type is `exact`.
```
  apply {
        smac.apply();
        if (dmac.apply().hit){
            //
        }
        else {
            broadcast.apply();
        }
    }
```
This command would apply the logic implemented in the `smac` for processing. The table will perform some processing based on the source MAC address. The corresponding actions will be performed based on the match result. The command `dmac.apply().hit` would check the result of the table using the ‘hit’ attribute. If there are matching entries found, the ‘if’ block will be executed, else it will invoke the `broadcast.apply()` to determine the multicast group for broadcast packets based on the ingress ports.

### 4. Egress Processing
```
control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
```
The control block `MyEgress` takes in 3 parameters: `inout headers hdr`, `inout metadata meta`, and `inout standard_metadata_t standard_metadata`.
```
    apply {
        // If ingress clone
        if (standard_metadata.instance_type == 1){
            hdr.cpu.setValid();
            hdr.cpu.srcAddr = hdr.ethernet.srcAddr;
            hdr.cpu.ingress_port = (bit<16>)meta.ingress_port;
            hdr.ethernet.etherType = L2_LEARN_ETHER_TYPE;
            truncate((bit<32>)22); //ether+cpu header
        }
    }
}
```
The apply block would check if the packet is an ingress clone. The if condition `standard_metadata.instance_type == 1` checks whether the `instance_type` field in the metadata is equals to 1 which represents ingress clone instance. If it is equal to 1, `hdr.cpu.setValid()` it would set the ‘valid’ flag in the ‘cpu’ header to true. This line `hdr.cpu.srcAddr = hdr.ethernet.srcAddr` would copy the source MAC address from the ‘ethernet’ header to the ‘cpu’ header. This line `hdr.cpu.ingress_port = (bit<16>)meta.ingress_port` sets the ingress port in the ‘cpu’ header to the value of 
`meta.ingress_port. hdr.ethernet.etherType = L2_LEARN_ETHER_TYPE`  would set the `etherType` field in the ‘ethernet’  header to be `L2_LEARN_ETHER_TYPE` which is defined at the beginning of the code. `truncate((bit<32>)22)` would ensure that the packet is truncated to 22 bytes in length.

