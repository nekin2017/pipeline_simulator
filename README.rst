ps.py:pipeline simulation
=========================

The node is a execution component that is defined with queue size and latency
(using step as unit).  the chain chains node as a line. The simulator is driven
by "step". We try to see how the executor stall and the change of the queue
unitilization.


spinlock.py: spin lock simulation
=================================

We assume there are n threads which share the same spinlock, we try to figure
out the behavior of the waiting queue

simple cpu
==========
this is a simple cpu simulator to show how cpu is work. see README.rst in the
directory for detail
