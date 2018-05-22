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
labels={} #all labels {name:pc}
ldl_rec=[] # [[pc, label_name]]
bzl_rec=[] # [[pc, label_name]]

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
        if tr<min or tr>12:
            raise Exception()
        return tr
    except:
            log_err("bad register operand %s"%(word), exit=True)

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
    
def ldl_coder(info, operand):
    global pc
    ldl_rec.append([pc, get_reg(operand[0]), operand[1]])
    output_buf.append(0)
    log_err("(pc=%x) ldl set tag"%(pc))
    pc+=1

def bnzl_coder(info, operand):
    global pc
    bzl_rec.append([pc, operand[0]])
    output_buf.append(0)
    log_err("(pc=%x) bzl set tag"%(pc))
    pc+=1

"""
ld <Tr> <imme>          #load
movi <Tr> <imme>        #move imme
st <Dr> <Ar>            #store data to address
inc <Tr>                #Tr+1
cmpi <Tr>, <immu>       #compare with imme
bnz <immu>               #relative branch to address
nop                     #no operation
halt                    #halt the cpu
data <imme_byte>...     #data definition
ldl <Tr> <lable>        #label version of ld
label <name>            #define label
bnzl <label>             #label version of bz
"""

inst_set = {
        'nop':  [0, com_coder],
        'ld':   [1, com_oti_coder],
        'movi': [2, com_oti_coder],
        'st':   [3, com_ots_coder],
        'inc':  [4, com_ot_coder],
        'cmpi': [5, com_oti_coder],
        'bnz':   [6, com_oi_coder],
        'halt': [7, com_coder],
        'data': [-1, data_coder],
        'ldl':  [-1, ldl_coder],
        'label':[-1, label_coder],
        'bnzl':  [-1, bnzl_coder]
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

#relacate label
for i in ldl_rec:
    if i[2] in labels:
        raddr=labels[i[2]]-i[0]
        raddr*=4
        inst=make_op_bytes(inst_set['ld'][0], i[1])
        inst[2:4]=raddr.to_bytes(2, 'little')
        output_buf[i[0]]=int.from_bytes(inst, 'little')
        log_err("relocate %x with %x"%(i[0], int.from_bytes(inst, 'little')))
    else:
        log_err("cannot find label %s"%(i[2]))

for i in bzl_rec:
    if i[1] in labels:
        raddr=labels[i[1]]-i[0]
        raddr*=4
        inst=make_op_bytes(inst_set['bnz'][0], 0)
        inst[2:4]=raddr.to_bytes(2, 'little', signed=True)
        output_buf[i[0]]=int.from_bytes(inst, 'little')
        log_err("relocate %x with %x"%(i[0], int.from_bytes(inst, 'little')))
    else:
        log_err("cannot find label %s"%(i[1]))

of = os.fdopen(sys.stdout.fileno(), "wb")
assert of
for i in range(0, pc):
    of.write(output_buf[i].to_bytes(4, 'little', signed=False))

log_err("success!")
