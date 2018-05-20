#!/usr/bin/python3

import sys
import os
from struct import pack

def default_coder(info, operand):
    print(info, operand)

inst_set = {
        'nop':  [0, default_coder],
        'ld':   [1, default_coder],
        'movi': [2, default_coder],
        'st':   [3, default_coder],
        'inc':  [4, default_coder],
        'cmpi': [5, default_coder],
        'bz':   [6, default_coder],
        'halt': [7, default_coder],
        'data': [-1, default_coder],
        'ldl':  [-1, default_coder],
        'label':[-1, default_coder],
        'bzl':  [-1, default_coder]
}

def log_err(msg, exit=False):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    if exit: sys.exit(-1)

def output(data):
    of.write(pack("i", data))

def output_inst_otss(op, tr, sr1, sr2):
    log_err("encode %d, %d, %d, %d"%(op, tr, sr1, sr2))
    of.write(pack("bbbb", op, tr, sr1, sr2))

def output_inst_otm(op, tr, imme):
    log_err("encode %d, %d, %d"%(op, tr, imme))
    of.write(pack("bbs", op, tr, imme))

def pharse_line(line):
    if not line.strip() or line.startswith("#"):
        return

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

of = os.fdopen(sys.stdout.fileno(), "wb")
assert of

for line in f.readlines():
    pharse_line(line.strip())
