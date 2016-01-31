#!/usr/bin/env python2
#
# disassemble the binary given as argv[1]
#
# output to stdout
#
from vmlib import vm
import sys

filename = sys.argv[1]

with open(filename, 'r') as fd:
    memimg = fd.read()

myVM = vm.VM(memimg)

for i in myVM.formattedListing():
    print i


