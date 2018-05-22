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

import matplotlib.pyplot as plt
import numpy as np

class node:

    def __init__(self, qsize, latency):
        self.qsize = qsize
        self.latency = latency
        self.qe_num = 0
        self.latency_step = -1 # -1-invalid, 0-first step finished, til latency-1 as the last step
        self.stall_h = []
        self.qe_num_h = []

        global ST_RUN, ST_INPUT_STALL, ST_OUTPUT_STALL
        ST_RUN=2
        ST_INPUT_STALL=1
        ST_OUTPUT_STALL=0

    def add_hist(self, status):
        self.stall_h.append(status)
        self.qe_num_h.append(self.qe_num)

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
                self.add_hist(ST_RUN)
                if self.latency_step == self.latency-1:
                    self.latency_step = -1
                    return True
                else:
                    return False
            else:
                self.add_hist(ST_INPUT_STALL)
                return False

        elif self.latency_step == self.latency -1:
            #stall last time, try again
            if can_output:
                #release it in self step
                self.latency_step = -1
                self.add_hist(ST_OUTPUT_STALL)
                return True
            else:
                #stall again
                self.add_hist(ST_OUTPUT_STALL)
                return False
        else:
            self.latency_step+=1
            self.add_hist(ST_RUN)
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
            print(i.stall_h, i.qe_num_h)

    def show_sum_graph(self, what=0):
        nn = len(self.nodes)
        i=0
        plt.subplots_adjust(hspace=0.8)
        for n in self.nodes:
            i+=1
            plt.subplot(nn, 1, i)

            plt.title(n.__str__())
            plt.ylabel("stall")
            plt.xlabel("step")

            if what == 0:
                x=np.arange(0, len(n.stall_h))
                y=np.array(n.stall_h)
                plt.ylim(-0.1, 2.1)
            else:
                x=np.arange(0, len(n.qe_num_h))
                y=np.array(n.qe_num_h)

            plt.plot(x, y)
            #plt.bar(x, y)
        plt.show()
        

c = chain([
    node(20, 3),
    node(30, 8),
    node(50, 2),
    node(64, 12),
    node(30, 60),
    ])

c.sim_run(10000)
c.show_sum_graph(0)
