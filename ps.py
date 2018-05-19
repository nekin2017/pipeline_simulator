#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np

class node:

    def __init__(self, qsize, latency):
        self.qsize = qsize
        self.latency = latency
        self.qe_num = 0
        self.latency_step = -1 # -1-invalid, 0-first step finished, til latency-1 as the last step
        self.stall = [] #0-run, 1-input_stall, 2-output_stall

    def __str__(self):
        return "node(%d, %d): qen=%d lat=%d"%(self.qsize, self.latency,
                self.qe_num, self.latency_step)

    def is_not_full(self):
        return self.qe_num<self.qsize-1

    def add_input(self):
        assert self.is_not_full()
        self.qe_num+=1

    def step(self, can_output=True):
        if self.latency_step == -1:
            if self.qe_num > 0:
                #get a new one to handle
                self.qe_num-=1
                self.latency_step = 0
                self.stall.append(0)
                if self.latency_step == self.latency-1:
                    self.latency_step = -1
                    return True
                else:
                    return False
            else:
                #input stall
                self.stall.append(1)
                return False

        elif self.latency_step == self.latency -1:
            #stall last time, try again
            if can_output:
                #release it in self step
                self.latency_step = -1
                self.stall.append(2) #not handle anything yet
                return True
            else:
                #stall again
                self.stall.append(2)
                return False
        else:
            self.latency_step+=1
            self.stall.append(0)
            if self.latency_step == self.latency-1 and can_output:
                self.latency_step = -1
                return True
            else:
                return False

class chain:
    def __init__(self, nodes):
        self.nodes = nodes
        assert len(nodes)>0
        self.output_num=0

    def sim_run(self, steps):
        for i in range(0, steps):
            #print("step %d: "%(i), end='')
            #self.show()
            self.step_on()

    def step_on(self):
        #fill first node
        if self.nodes[0].is_not_full():
            self.nodes[0].add_input()

        #exec node and fill next node
        nn = len(self.nodes)
        if nn==1:
            if self.nodes[0].step(True):
                self.output_num+=1
        else:
            for i in range(0, nn-1):
                ret = self.nodes[i].step(self.nodes[i+1].is_not_full())
                if ret:
                    self.nodes[i+1].add_input()

            if self.nodes[nn-1].step():
                self.output_num+=1

    def show(self):
        for i in self.nodes:
            print(i, end=' ')
        print()

    def show_sum_text(self):
        print("sum:", self.output_num)
        for i in self.nodes:
            print(i.stall)

    def show_sum_graph(self):
        nn = len(self.nodes)
        i=0
        for n in self.nodes:
            i+=1
            plt.subplot(nn, 1, i)
            x=np.arange(0, len(n.stall))
            y=np.array(n.stall)
            plt.plot(x, y)
            plt.title(n.__str__())
            plt.ylabel("stall")
            plt.xlabel("step")
        plt.show()
        

c = chain([
    node(3, 3),
    node(4, 4),
    node(5, 2),
    node(5, 12),
    node(3, 6),
    ])

c.sim_run(1000)
c.show_sum_graph()
