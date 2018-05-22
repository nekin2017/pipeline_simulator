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

global ST_WAIT_LOCK, ST_IN_LOCK, ST_OUT_LOCK
ST_OUT_LOCK = 2
ST_IN_LOCK = 1
ST_WAIT_LOCK = 0

class lock:
    def __init__(self):
        self.current_holder = None

    def try_lock(self, thread):
        #note: need queue thread in the future
        if self.current_holder:
            return False
        else:
            self.current_holder = thread
            return True

    def unlock(self, thread):
        assert thread == self.current_holder 
        self.current_holder = None

class thread:

    def __init__(self, out_lock_step, in_lock_step, lock, deviate=0.1):

        assert deviate >= 0 and deviate < 1
        self.out_lock_step = out_lock_step
        self.in_lock_step = in_lock_step
        self.deviate = deviate
        self.lock = lock

        self.cur_out_lock_step = self.randomized(self.out_lock_step)
        self.cur_in_lock_step = self.randomized(self.in_lock_step)
        self.hist_status = []
        self.current_status=ST_OUT_LOCK

    def randomized(self, input=1):
        "return a randomized value: 1 +/- deviate * rand[0-1)"
        dev = 1.0 - self.deviate + self.deviate * np.random.random() * 2
        return int(dev*input)

    def add_hist(self, status):
        self.hist_wait.append(status)

    def __str__(self):
        return "thread(%d, %d)"%(self.out_lock_step, self.in_lock_step)

    def switch(self, new_status):
        if new_status == ST_OUT_LOCK:
            self.cur_out_lock_step = self.randomized(self.out_lock_step)
            assert self.current_status == ST_IN_LOCK
        elif new_status == ST_IN_LOCK:
            self.cur_in_lock_step = self.randomized(self.in_lock_step)
            assert self.current_status in [ST_WAIT_LOCK, ST_OUT_LOCK]
        else:
            assert new_status == ST_WAIT_LOCK
            assert self.current_status in [ST_WAIT_LOCK, ST_OUT_LOCK]
        self.current_status = new_status

    def step(self):
        #print("%d(%d,%d)"%(self.current_status, self.cur_out_lock_step, self.cur_in_lock_step))
        if self.current_status == ST_OUT_LOCK:
            self.cur_out_lock_step-=1
            if not self.cur_out_lock_step:
                if self.lock.try_lock(self):
                    self.switch(ST_IN_LOCK)
                else:
                    self.switch(ST_WAIT_LOCK)
        elif self.current_status == ST_IN_LOCK:
            self.cur_in_lock_step-=1
            if not self.cur_in_lock_step:
                self.lock.unlock(self)
                self.switch(ST_OUT_LOCK)
        else:
            assert self.current_status == ST_WAIT_LOCK
            if self.lock.try_lock(self):
                self.switch(ST_IN_LOCK)
                self.cur_in_lock_step -= 1
                if not self.cur_in_lock_step:
                    self.lock.unlock(self)
                    self.switch(ST_OUT_LOCK)
            else:
                assert self.current_status == ST_WAIT_LOCK

        self.hist_status.append(self.current_status)

class executor:
    def __init__(self, threads):
        self.threads = threads

    def sim_run(self, steps):
        for i in range(0, steps):
            self.step_on()

    def step_on(self):
        for i in self.threads:
            i.step()

    def show(self):
        for i in self.thread:
            print(i, end=' ')
        print()

    def get_queue_len(self):
        qlen = []
        for i in range(0, len(self.threads[0].hist_status)):
            ql = 0
            for n in self.threads:
                if n.hist_status[i] == ST_WAIT_LOCK:
                    ql+=1
            qlen.append(ql)
        return qlen

    def show_threads_status(self, graph=False):
        i=0
        nn = len(self.threads)

        if graph:
            plt.subplots_adjust(hspace=0.8)

        for n in self.threads:
            i+=1
            print(n.hist_status)
            if graph:
                plt.subplot(nn, 1, i)

                plt.title(n.__str__())
                plt.ylabel("stall")
                plt.xlabel("step")

                x=np.arange(0, len(n.hist_status))
                y=np.array(n.hist_status)
                plt.ylim(-0.1, 2.1)

                plt.plot(x, y)

        if graph:
            plt.show()

    def get_percentage(self, data, value):
        sum = 0
        for i in data:
            if i==value:
                sum+=1
        return sum/len(data)

    def show_wait_status(self, graph=False, sum_only=True):
        qls= self.get_queue_len()

        if not sum_only:
            print(qls)
            if graph:
                plt.title("queue len procedure")
                plt.xlabel("step")
                plt.ylabel("queue len")
                x=np.arange(0, len(qls))
                y=np.array(qls)
                plt.plot(x, y)
                plt.show()

        print(self.get_percentage(qls, 0)*100, "percent is free")


for i in range(1, 30):
    lock1 = lock()
    threads = []
    for j in range(0, i):
        threads.append(thread(1000, 10, lock1))

    exe = executor(threads)
    exe.sim_run(10000)
    print(i, "threads test:", end='')
    exe.show_wait_status()

#exe.show_thread_status(graph=True)
