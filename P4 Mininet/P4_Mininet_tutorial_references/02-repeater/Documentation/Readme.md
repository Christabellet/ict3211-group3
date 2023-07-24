## Explanation of the code
#### #### The objective of this exercise is to create a basic topology with host and p4 switches along with adding links connecting them together. Implementing a p4 program to enable switches to bounce back packets to the interface that they came from.

In this exercise, you would require 3 files as shown below, 

| File | Description |
| --- | --- |
| `p4app.json` | creates the topology of the network diagram |
| `reflector.p4` | p4 program that defines how packets should flow in a network diagram |
| `s1-commands.txt` | forwarding entries to table |

In the repeater_without_tables.p4 file,  

### 1. Parser
```
parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) 
```
The parser block `MyParser` takes in 4 parameters `packet_in packet`, `out headers hdr`, `inout metadata meta`, and `inout standard_metadata_t standard_metadata`. 
```
      state start{
          transition accept;
```
This command defines the start of the parser. It represents the transmission of the packet into the ‘accept’ state. 

### 1. Ingress Processing
```
control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) 
```
The control block `MyIngress` takes in 3 parameters `inout headers hdr`, `inout metadata meta` and `inout standard_metadata_t standard_metadata`. 
```
    apply {
        // If input port is 1 => output port 2
        if (standard_metadata.ingress_port == 1){
            standard_metadata.egress_spec = 2;
        }

        // If input port is 2 => output port 1
        else if (standard_metadata.ingress_port == 2){
            standard_metadata.egress_spec = 1;
        }
    }
```
The `apply()` function will ensure that all the packet is processed with the logic implemented. The logic is to ensure that if the packet is received from port one then it should leave from port 2 and vice versa. 
```
        if (standard_metadata.ingress_port == 1){
            standard_metadata.egress_spec = 2;
        }

```
This command checks if the ingress port which is the port that the packet is received is equal to port 1. If yes, it would set the egress port which is the port that the packet will leave the switch. 

Apart from the `repeater_without_table.p4`, you will also need the `s1_command.txt` to populate the forwarding entries in the switch. 
```
table_add repeater forward 1 => 2
table_add repeater forward 2 => 1
```
This command adds an entry to the ‘repeater’ table and it instructs the switch to forward if it receives a packet with ingress port 1 and forward it to egress port 2. Vice Versa to forward if it receives a packet with ingress port 2 and `forward` it to egress port 1.  
