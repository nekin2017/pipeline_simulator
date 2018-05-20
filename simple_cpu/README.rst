simple cpu
==========

definition
----------

register files
``````````````
(word wide: 32bit, little endian)
r0=0
r1-r12
r13-pc
r14-lr-link register
r15-st-cpu state: bit0-zero

instruction set
````````````````

ld <Tr> <imme>          #load
movi <Tr> <imme>        #move imme
st <Dr> <Ar>            #store data to address
inc <Tr>                #Tr+1
cmpi <Sr>, <immu>       #compare with imme
bz <immu>               #relative branch to address
nop                     #no operation
halt                    #halt the cpu

pseudo code
```````````
data <imme_byte>...     #data definition
ldl <Tr> <lable>        #label version of ld
label <name>            #define label
bzl <label>             #label version of bz


instruction encoding
````````````````````

bytes[0] operation code
        0       nop
        1       ld
        2       movi
        3       st
        4       inc
        5       cmpi
        6       bz
        7       halt

bytes[1] reserved
bytes[2] register1 register2
bytes[3] register3 register4
bytes[2:3] imme


memory space
`````````````
0-4095 memory
4096-8192 io space
others are invalid

reset vector
````````````
address 0
