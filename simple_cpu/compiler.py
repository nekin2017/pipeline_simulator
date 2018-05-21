#!/usr/bin/python3

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
    log_err("data -> %d"%(data))
    output_buf.append(data)
    pc+=1

def output_inst_otss(op, tr, sr1, sr2):
    global pc
    inst=op<<8*3
    inst|=tr<<8*2
    inst|=sr1<<8
    inst|=sr2
    log_err("%d, %d, %d, %d -> %x"%(op, tr, sr1, sr2, inst))
    output_buf.append(inst)
    pc+=1

def output_inst_otm(op, tr, imme):
    global pc
    inst=op<<8*3
    inst|=tr<<8*2
    inst|=imme
    log_err("%d, %d, %d -> %x"%(op, tr, imme, inst))
    output_buf.append(inst)
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
    output_inst_otm(info[0], get_reg(operand[0]), get_imme(operand[1]))

def com_ots_coder(info, operand):
    output_inst_otss(info[0], get_reg(operand[0]), get_reg(operand[1], Tr=False), 0)

def com_ot_coder(info, operand):
    output_inst_otss(info[0], get_reg(operand[0]), 0, 0)

def com_oi_coder(info, operand):
    output_inst_otm(info[0], 0, get_imme(operand[0]))

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
    ldl_rec.append([pc, get_reg(operand[0]), operand[1]])
    output_buf.append(0)
    pc+1

def bzl_coder(info, operand):
    bzl_rec.append([pc, operand[0]])
    output_buf.append(0)
    pc+1

"""
ld <Tr> <imme>          #load
movi <Tr> <imme>        #move imme
st <Dr> <Ar>            #store data to address
inc <Tr>                #Tr+1
cmpi <Sr>, <immu>       #compare with imme
bz <immu>               #relative branch to address
nop                     #no operation
halt                    #halt the cpu
data <imme_byte>...     #data definition
ldl <Tr> <lable>        #label version of ld
label <name>            #define label
bzl <label>             #label version of bz
"""

inst_set = {
        'nop':  [0, com_coder],
        'ld':   [1, com_oti_coder],
        'movi': [2, com_oti_coder],
        'st':   [3, com_ots_coder],
        'inc':  [4, com_ot_coder],
        'cmpi': [5, com_oti_coder],
        'bz':   [6, com_oi_coder],
        'halt': [7, com_coder],
        'data': [-1, data_coder],
        'ldl':  [-1, ldl_coder],
        'label':[-1, label_coder],
        'bzl':  [-1, bzl_coder]
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
        output_buf[i[0]]=inst_set['ld'][0]<<8*3
        output_buf[i[0]]|=i[1]<<8*2
        output_buf[i[0]]|=raddr
    else:
        log_err("cannot find label %s"%(i[2]))

for i in bzl_rec:
    if i[1] in labels:
        raddr=labels[i[1]]-i[0]
        output_buf[i[0]]=inst_set['bz'][0]<<8*3
        output_buf[i[0]]|=0
        output_buf[i[0]]|=raddr
    else:
        log_err("cannot find label %s"%(i[1]))

of = os.fdopen(sys.stdout.fileno(), "wb")
assert of
for i in range(0, pc):
    of.write(output_buf[i].to_bytes(4, 'little', signed=True))

log_err("success!")
