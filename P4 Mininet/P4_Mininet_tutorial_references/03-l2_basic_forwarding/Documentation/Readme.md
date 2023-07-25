## Explanation of the code
#### #### The objective of this exercise is to implement basic layer 2 forwarding. In order to implement forwarding, a switch would be required to know which port it can find a given MAC address for it to forward to. 

In this exercise, you would require 3 files as shown below, 
| File | Description |
| --- | --- |
| `p4app.json` | creates the topology of the network diagram |
| `reflector.p4` | p4 program that defines how packets should flow in a network diagram |
| `s1-commands.txt` | forwarding entries to table |

In the l2_basic_forwarding.p4 file, 

### 1. Ingress Processing
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
This action `drop()` is called when the control logic decides to drop the packet. It calls the `mark_to_drop` function which passes in the standard_metadata as an argument. 
```
    action forward(bit<9> egress_port) {
        standard_metadata.egress_spec = egress_port;
    }
```
This action `forward(bit<9> egress_port)` is called when the control logic decides to forward the packet. It takes in a 9 bit argument, `egress_port`.  It sets the `standard_metadata.egress_spec` to the specified egress_port. 
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

There are 2 possible actions to be taken.
```
        actions = {
            forward;
            NoAction;
        }
        size = 256;
        default_action = NoAction;
```
`Forward`: If there is a matching entry in the table, this action will be applied.
`NoAction`: If there is no matching entry in the table, this action will be default which indicates no forwarding is done. 

The `size` parameter defines the maximum number of entries the table can hold. In this example, the table has a size of 256. 

These entries will be stored in the `s1_commands.txt`.  
```
table_add dmac forward 00:00:0a:00:00:01 => 1
table_add dmac forward 00:00:0a:00:00:02 => 2
table_add dmac forward 00:00:0a:00:00:03 => 3
table_add dmac forward 00:00:0a:00:00:04 => 4
```
Each `table_add` command specifies a MAC address and the corresponding egress port to which that MAC address should be forwarded. 

For example, `table_add dmac forward 00:00:0a:00:00:01 => 1`
This command adds an entry to the `dmac` table. The destination MAC address would be `00:00:0a:00:00:01`. The action associated with it is `forward`. The egress port that the forward action will forward the packet to is port of value `1`.
```
    apply {
        dmac.apply();
    }
```
This command would apply the logic implemented in the `dmac` for processing. When this statement is executed, the table `dmac` will attempt to match the destination MAC address of the packet with its entries and apply the appropriate actions based on the results. 














