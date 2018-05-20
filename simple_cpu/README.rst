simple cpu
==========

definition
----------

register files
``````````````
(word wide: 32bit, little endian)
r0=0
r1
r2
r3
r4
pc
lr-link register
st-cpu state

instruction set
````````````````

ld <Tr>, <Sr>
mov <Tr>, <Sr>
movih <Tr>, <imme>
movil <Tr>, <imme>
xor <Tr>, <Sr1>, <Sr2>
halt


psudeo code
```````````
data <imme32>


instruction encoding
````````````````````

code[0:5] instruction
        00000 nop
        00001 halt
        001xx ld
        01001 mov
        01010 movih
        01011 movil
        01100 xor

code[6:8] condition
code[9:11] <Tr>
code[12:14] <Sr1>
code[14:16] <Sr2>
code[17:32] imme


memory space
`````````````
0-4096 are valid
