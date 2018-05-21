#test assample file for simple cpu

ldl 1 data
label loop
movi 2 0x100
st 2 1
inc 1
cmpi 1 10
bzl loop
halt

label data
data 0x12345678 0x12 0x33
data 1
