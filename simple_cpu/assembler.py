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
import os
from struct import pack

pc=0
output_buf=[]
labels={}  #all labels {name:pc}
rec_tab=[] # [[pc, op, tr, label_name]]

def log_err(msg, exit=False):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    if exit: sys.exit(-1)

def output_data(data):
    global pc
    log_err("(pc=%x) data -> %d"%(pc, data))
    output_buf.append(data)
    pc+=1

def make_op_bytes(op, tr):
    inst=bytearray(4)
    inst[0]=op
    inst[1]=tr
    return inst

def output_inst_otss(op, tr, sr1, sr2):
    global pc
    inst=make_op_bytes(op, tr)
    inst[2]=sr1
    inst[3]=sr2
    log_err("(pc=%x) %d, %d, %d, %d -> %x"%(pc, op, tr, sr1, sr2, int.from_bytes(inst, 'little')))
    output_buf.append(int.from_bytes(inst, 'little'))
    pc+=1

def output_inst_oti(op, tr, imme):
    global pc
    inst=make_op_bytes(op, tr)
    inst[2:4]=imme.to_bytes(2, 'little')
    log_err("(pc=%x) %d, %d, %d -> %x"%(pc, op, tr, imme, int.from_bytes(inst, 'little')))
    output_buf.append(int.from_bytes(inst, 'little', signed=False))
    pc+=1

def get_reg(word, Tr=False):
    min=0
    if Tr:
        min=1

    try:
        tr=int(word)

        log_err("tr=%d"%(tr))
        if tr<min or tr>12:
            raise Exception()
        return tr
    except:
            log_err("bad register id %s"%(word), exit=True)

def get_imme(word):
    try:
        imme=int(word, 0)
        if imme<-0x7fff or imme>0x7fff:
            raise Exception()
        return imme
    except:
            log_err("bad imme %s"%(word), exit=True)

def com_coder(info, operand):
    output_inst_otss(info[0], 0, 0, 0)

def com_oti_coder(info, operand):
    output_inst_oti(info[0], get_reg(operand[0]), get_imme(operand[1]))

def com_ots_coder(info, operand):
    output_inst_otss(info[0], get_reg(operand[0]), get_reg(operand[1], Tr=False), 0)

def com_ot_coder(info, operand):
    output_inst_otss(info[0], get_reg(operand[0]), 0, 0)

def com_oi_coder(info, operand):
    output_inst_oti(info[0], 0, get_imme(operand[0]))

def data_coder(info, operand):
    try:
        for i in operand:
            d = int(i, 0)
            output_data(d)
    except:
        log_err("bad data", exit=True)

def label_coder(info, operand):
    l=operand[0]
    if l in labels:
        log_err("dup label: %s"%(l), exit=True)

    labels[l] = pc

def labeli_coder(info, operand):
    global pc
    if info[2]:
        rec_tab.append([pc, info[3], get_reg(operand[0]), operand[1], info[4]])
    else:
        rec_tab.append([pc, info[3], 0, operand[0], info[4]])
    output_buf.append(0)
    log_err("(pc=%x) set relocate item"%(pc))
    pc+=1

"""
ld <Tr> <Ar>            #load
movi <Tr> <imme>        #move imme
st <Dr> <Ar>            #store data to address
inc <Tr>                #Tr+1
cmpi <Tr>, <immu>       #compare with imme
bnz <immu>              #relative branch to address
nop                     #no operation
halt                    #halt the cpu
data <imme_byte>...     #data definition
ldl <Tr> <lable>        #label version of ld
label <name>            #define label
bnzl <label>            #label version of bnz
movil <Tr> <label>      #label version of movi
"""

# [ op : [opcode, coder]
# [ psudeo : [opcode, coder, with_tr, read_opcode, is_abs_addr]
inst_set = {
        'nop':  [0, com_coder],
        'ld':   [1, com_ots_coder],
        'movi': [2, com_oti_coder],
        'st':   [3, com_ots_coder],
        'inc':  [4, com_ot_coder],
        'cmpi': [5, com_oti_coder],
        'bnz':   [6, com_oi_coder],
        'halt': [7, com_coder],
        'data': [-1, data_coder],
        'label':[-1, label_coder],
        'bnzl':  [-1, labeli_coder, False, 'bnz', False],
        'movil': [-1, labeli_coder, True, 'movi', True]
}

def pharse_line(line):
    if not line.strip() or line.startswith("#"):
        return

    log_err("encode: %s"%(line))
    words = line.split()
    op=words[0].strip()
    info=inst_set[op]
    if info:
        coder=info[1](info, words[1:])
    else:
        log_err("invalid code: %s"%(line), exit=True)

if len(sys.argv) != 2:
    log_err("usage: %s <input.s>"%(sys.argv[0]), exit=True)

f = open(sys.argv[1])
if not f:
    log_err("cannot open inptut file", exit=True)

for line in f.readlines():
    pharse_line(line.strip())

#relacate label [[pc, op, tr, label_name, is_abs_addr]]
for i in rec_tab:
    rpc=i[0]; rop=i[1]; rtr=i[2]; rlabel=i[3]; ris_abs_addr=i[4]
    if rlabel in labels:
        if ris_abs_addr:
            raddr=labels[rlabel]
        else:
            raddr=labels[rlabel]-rpc
        raddr*=4
        inst=make_op_bytes(inst_set[rop][0], rtr)
        inst[2:4]=raddr.to_bytes(2, 'little', signed=True)
        output_buf[rpc]=int.from_bytes(inst, 'little')
        log_err("reloc %x (label=%s on 0x%x) with inst(%x)"%(rpc, rlabel,
            labels[rlabel], output_buf[rpc]))
    else:
        log_err("cannot find label %s"%(i[3]), exit=True)

of = os.fdopen(sys.stdout.fileno(), "wb")
assert of
for i in range(0, pc):
    of.write(output_buf[i].to_bytes(4, 'little', signed=False))

log_err("success!")
