#!/usr/bin/python3

"""
  Copyright (C) 2018 Kenneth Lee. All rights reserved.

 TLicensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import sys

def log_err(msg, exit=False):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    if exit: sys.exit(-1)

def log(msg):
    #sys.stderr.write(msg)
    #sys.stderr.write("\n")
    pass

"""
ld <Tr> <imme>          #load
movi <Tr> <imme>        #move imme
st <Dr> <Ar>            #store data to address
inc <Tr>                #Tr+1
cmpi <Sr>, <immu>       #compare with imme
bz <immu>               #relative branch to address
nop                     #no operation
halt                    #halt the cpu
"""

def op_nop(cpu, inst):
    log("nop")
    return 4

def op_ld(cpu, inst):
    tr=inst[1]
    addr=cpu.pc+int.from_bytes(inst[2:4], 'little', signed=True)
    cpu.reg[tr]=int.from_bytes(cpu.mem[addr:addr+4], 'little', signed=False)
    log("load from 0x%x(0x%x) to r%d"%(addr, cpu.reg[tr], tr))
    return 4

def op_movi(cpu, inst):
    tr=inst[1]
    imme=cpu.pc+int.from_bytes(inst[2:4], 'little', signed=True)
    cpu.reg[tr]=imme
    log("set 0x%x to r%d"%(cpu.reg[tr], tr))
    return 4

def op_st(cpu, inst):
    tr=inst[1]
    sr=inst[2]
    addr=cpu.reg[sr] 
    if addr < 0 or addr > 8192:
        log_err("segment fault on address 0x%x"%(cpu.reg[sr]), exit=True)

    if addr >= 4096:
        print("io(0x%x)!"%(cpu.reg[tr]))
    else:
        cpu.mem[addr:addr+4]=tr.to_bytes(4, 'little')
        log("store r%d(0x%x) to 0x%x"%(tr, cpu.reg[tr], addr))

    return 4

def op_inc(cpu, inst):
    tr=inst[1]
    cpu.reg[tr]+=1
    log("inc r%d to 0x%x"%(tr, cpu.reg[tr]))
    return 4

def op_cmpi(cpu, inst):
    tr=inst[1]
    imme=cpu.pc+int.from_bytes(inst[2:4], 'little', signed=True)
    cpu.pstate &= 0
    if cpu.reg[tr] > imme:
        cpu.pstate |= 0x2 #bigger than bit
    elif cpu.reg[tr] == imme:
        cpu.pstate |= 0x1 #zero bit

    log("compare r%d(0x%x) with 0x%x, pstate=0x%x"%(tr, cpu.reg[tr], imme, cpu.pstate))
    return 4

def op_bnz(cpu, inst):
    imme=int.from_bytes(inst[2:4], 'little', signed=True)
    if cpu.pstate & 0x1:
        log("branch untaken")
        return 4
    else:
        log("branch to %x"%(imme))
        return imme

def op_halt(cpu, inst):
    log("halt")
    sys.exit(0)


inst_set = [
    ['nop', op_nop],
    ['ld', op_ld],
    ['movi', op_movi],
    ['st', op_st],
    ['inc', op_inc],
    ['cmpi', op_cmpi],
    ['bnz', op_bnz],
    ['halt', op_halt]
]

class cpu:
    def __init__(self):
        self.pc=0
        self.reg=[0]*12
        self.pstate = 0

    def load_program(self, path):
        f = open(path, mode='rb')
        self.mem=f.read()
        f.close()

    def fetch(self):
        global inst_set

        if self.pc<0 or self.pc>4096:
            log_err("sys abort due to invalid pc: %d"%(self.pc), exit=True)

        op = self.mem[self.pc]
        if op >= len(inst_set):
            log_err("sys abort due to invalid inst op: %x"%(op), exit=True)

        return self.mem[self.pc:self.pc+4]


    def run(self, max_step):
        i=0
        while(i<max_step):
            inst = self.fetch()
            self.pc+=inst_set[inst[0]][1](self, inst)
            i+=1
        log_err("cpu too hot (%d), exit"%(max_step), exit=True)



if len(sys.argv) != 2:
    log_err("usage: %s <images>"%(sys.argv[0]), exit=True)

c=cpu()
c.load_program(sys.argv[1])
c.run(1000)
