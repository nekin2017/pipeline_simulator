#test assample file for simple cpu

ldl 1 data
label loop
movi 2 0x10000
st 2 1
inc 1
cmpi 1, 10
bz loop
halt

label data
data 0x12 34 56 78 12
data 1
