simple cpu
==========

definition
----------

register files
``````````````

(word wide: 32bit, little endian)
::
        r0=0
        r1-r12
        r13-pc
        r14-lr-link register
        r15-st-cpu state: bit0-zero bit1-bigger than

instruction set
````````````````
::

        ld <Tr> <imme>          #load
        movi <Tr> <imme>        #move imme
        st <Dr> <Ar>            #store data to address
        inc <Tr>                #Tr+1
        cmpi <Tr>, <immu>       #compare with imme
        bnz <immu>              #relative branch to address if non-zore
        nop                     #no operation
        halt                    #halt the cpu

pseudo code
```````````
::

        data <imme_byte>...     #data definition
        label <name>            #define label
        bnzl <label>            #label version of bnz
        movil <label>           #label version of movi


instruction encoding
````````````````````

bytes[0] operation code::

        0       nop
        1       ld
        2       movi
        3       st
        4       inc
        5       cmpi
        6       bnz
        7       halt


* bytes[1] output_register
* bytes[2] input_register1
* bytes[3] input_register2
* bytes[2,3] imme


memory space
`````````````
* 0-4095: memory
* 4096-8192: io space
  0: output
  4: input
* others are invalid

interrupt vector
````````````````
* 0:       system reset
* 1024:    input port interrupt
