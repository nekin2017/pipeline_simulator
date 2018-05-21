#!/usr/bin/python3

import sys

def log_err(msg, exit=False):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    if exit: sys.exit(-1)

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

inst_set = [
    ['nop'],
    ['ld'],
    ['movi'],
    ['st'],
    ['inc'],
    ['cmpi'],
    ['bz'],
    ['halt']
]

class cpu:
    def __init__(self):
        self.pc=0
        self.reg=[0]*12

    def load_program(self, path):
        f = open(path, mode='rb')
        self.mem=f.read()
        f.close()
        print("load program: ")
        n=1
        for i in self.mem:
            print("%2x "%(i), end='')
            if not n%(4*8):
                print()
            elif not n%4:
                print("-", end='')
            n+=1
        print("\nend")

    def fetch(self):
        global inst_set

        if self.pc<0 or self.pc>4096:
            log_err("sys abort due to invalid pc: %d"%(self.pc), exit=True)

        op = self.mem[self.pc+3]
        try:
            log_err("decode %s"%(inst_set[op][0]))
        except:
            log_err("sys abort due to invalid inst op: %x"%(op), exit=True)
        self.pc+=4

    def run(self):
        while(True):
            inst = self.fetch()



if len(sys.argv) != 2:
    log_err("usage: %s <images>"%(sys.argv[0]), exit=True)

c=cpu()
c.load_program(sys.argv[1])
c.run()
