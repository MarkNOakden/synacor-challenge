#!/usr/bin/env python2
#
# wrapper script ot run the challenge from the start
#
from vmlib import vm
from maputils import room


fd = open('challenge.bin', 'rb')
challenge_raw = fd.read()
fd.close()

myVM = vm.VM(prog=challenge_raw)

# myVM.dump()
myVM.run()
#myVM.dump()



