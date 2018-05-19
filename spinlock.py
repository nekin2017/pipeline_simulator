#!/usr/bin/python3

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

    def show_sum_text(self):
        for i in self.threads:
            print(i.hist_status)
        #todo: wait queue len

    def show_sum_graph(self):
        nn = len(self.threads)
        i=0
        plt.subplots_adjust(hspace=0.8)
        for n in self.threads:
            i+=1
            plt.subplot(nn, 1, i)

            plt.title(n.__str__())
            plt.ylabel("stall")
            plt.xlabel("step")

            x=np.arange(0, len(n.hist_status))
            y=np.array(n.hist_status)
            plt.ylim(-0.1, 2.1)

            plt.plot(x, y)
            #plt.bar(x, y)
        plt.show()
        #todo: wait queue len
        

lock1 = lock()

exe = executor([
    thread(50, 3, lock1),
    thread(60, 2, lock1),
    thread(60, 2, lock1),
    thread(60, 6, lock1),
    ])

exe.sim_run(1000)
#exe.show_sum_text()
exe.show_sum_graph()
