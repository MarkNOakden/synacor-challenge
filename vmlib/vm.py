#!/usr/bin/env python2
#
# vm implementation for the synacor challenge
#
# started 6.1.2016
import sys
import itertools
import shlex

from exceptions import IndexError

class VmException(Exception): pass
class VmStop(VmException): pass
class VmUnimplemented(VmException): pass
class VmBadOpcode(VmException): pass
class VmInvalidValue(VmException): pass
    
class wordarray(object):
    def __init__(self, s = None):
        if s is None:
            self.data = bytearray()
        else:
            self.data = bytearray(s)

    def __getitem__(self, index):
        if isinstance(index, slice):
            results = []
            start = 0 if index.start is None else index.start*2
            stop = len(self.data)/2 if index.stop is None else index.stop*2
            step = 2 if index.step is None else index.step*2
            for i in range(start, stop, step):
                l, h = self.data[i], self.data[i+1]
                results.append((h << 8) + l)
            return results
        else:
            l, h = self.data[index*2], self.data[index*2+1]
            return (h << 8) + l

    def index(self, s, start = 0):
        s = ''.join(map(''.join, zip(itertools.repeat(chr(0)), s)))
        return self.data.index(s, start*2)/2

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            raise IndexError('Can\'t set slices on wordarray objects')
        value = value % VM.MAXINT
        h = value >> 8
        l = value & 255
        self.data[index*2:index*2+2] = [l, h]

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)
        
        
class VM(object):
    REGISTERS = 8
    MEMSIZE = 32768
    MAXINT = 32768
    INTMASK = MAXINT - 1

    useAlphaRegnames = True
    RNAMES = 'ABCDEFGH'
    
    # opcode: (name, argumentCount)
    operators = {
        0: ('halt', 0),
        1: ('set', 2),
        2: ('push', 1),
        3: ('pop', 1),
        4: ('eq', 3),
        5: ('gt', 3),
        6: ('jmp', 1),
        7: ('jt', 2),
        8: ('jf', 2),
        9: ('add', 3),
        10: ('mult', 3),
        11: ('mod', 3),
        12: ('and', 3),
        13: ('or', 3),
        14: ('not', 2),
        15: ('rmem', 2),
        16: ('wmem', 2),
        17: ('call', 1),
        18: ('ret', 0),
        19: ('out', 1),
        20: ('in', 1), 
        21: ('noop', 0)
    }

    addrfmt = '{:0>5}: {}'
    opcodefmt = '{:>4} {}'
    
    def __init__(self, prog = None):
        self.stack = []
        self.pc = 0
        self.instructionCount = 0
        self.memory = wordarray('\0' * VM.MEMSIZE * 2)
        self.registers = wordarray('\0' * VM.REGISTERS * 2)
        self.breakpoints = set()
        self.watchpoints = set()
        self.inputbuffer = '' # for keyboard input
        if prog is not None:
            self.memory.data[0:len(bytearray(prog))] = bytearray(prog)
        self.inputlog = ''

    def store(self, addr, val):
        if self.isMemory(addr):
            self.memory[addr] = val
        elif self.isRegister(addr):
            self.registers[addr - VM.MAXINT] = val
        else:
            raise VmInvalidValue('address {} is neither memory nor register'.format(addr))
        if addr in self.watchpoints:
            print 'Watchpoint at {} triggered by write of {}'.format(addr, val)
            self.debug()

    # def run(self):
    #     try:
    #         while True:
    #             if self.pc in self.breakpoints:
    #                 print 'Breakpoint at {} triggered'.format(self.pc)
    #                 self.debug()
    #             else:
    #                 self.step()
    #     except VmStop:
    #         raise
    #     except KeyboardInterrupt:
    #         self.debug()
    #         return

    def run(self):
        while True:
            if self.pc in self.breakpoints:
                print 'Breakpoint at {} triggered'.format(self.pc)
                self.debug()
            else:
                try:
                    self.step()
                except VmStop:
                    raise
                except KeyboardInterrupt:
                    self.debug()

        
        
    def step(self):
        opcode = self.memory[self.pc]

        try:
            opname, nargs = VM.operators[opcode]
        except IndexError:
            raise VmBadOpcode('Bad Opcode {:d} at address {:d}'.format(current, self.pc))

        try:
            operator = getattr(self, '_'+opname)
        except AttributeError:
            raise VmUnimplemented('Unimplemented operation {}'.format(opname))

        args = self.memory[self.pc+1:self.pc+1+nargs]
        self.pc += 1 + nargs

        self.instructionCount += 1
        
        operator(*args)

    ##################################################################
    # Debugger functions
    ##################################################################
    def debug(self, scriptline=None):
        print 'Entering Debugger'
        self.dump()
        while True:
            sys.stdout.write('dbg> ')
            if scriptline is None:
                cmd = sys.stdin.readline()
            else:
                cmd = scriptline
            cmdlist = shlex.split(cmd)
            if cmd[0] == '$':
                if cmd[1] == 'l':
                    try:
                        addr = int(cmd[2:].strip())
                    except (ValueError, IndexError):
                        addr = self.pc
                    for i, j in self.listing(addr, 20):
                        if i == self.pc:
                            pcind = '->'
                        else:
                            pcind = '  '
                        bpind = ' '
                        if i in self.breakpoints:
                            bpind = 'B'
                        else:
                            bpind = ' '
                        if i in self.watchpoints:
                            bpind += 'W'
                        else:
                            bpind += ' '
                        print ('{} {} ' + VM.addrfmt).format(pcind, bpind,
                                                        i, j)
                elif cmd[1] == 's':
                    print self.instr(self.pc)
                    self.step()
                elif cmd[1] == 'r':
                    if self.pc in self.breakpoints:
                        # required otherwise $r from a breakpoint
                        # doesn't resume
                        self.step()
                    #self.run()
                    return
                elif cmd[1] == 'd':
                    self.dump()
                elif cmd[1] == 'm':
                    self.memdump()
                elif cmd[1] == 'b':
                    try:
                        addr = int(cmd[2:].strip())
                    except (ValueError, TypeError):
                        self.showbreakpoints(self.breakpoints)
                    else:
                        self.addbreakpoint(addr, self.breakpoints)
                elif cmd[1] == 'u':
                    try:
                        addr = int(cmd[2:].strip())
                    except (ValueError, TypeError):
                        self.clearbreakpoints(self.breakpoints)
                    else:
                        self.rmbreakpoint(addr, self.breakpoints)
                elif cmd[1] == 'w':
                    try:
                        addr = int(cmd[2:].strip())
                    except (ValueError, TypeError):
                        self.showbreakpoints(self.watchpoints)
                    else:
                        self.addbreakpoint(addr, self.watchpoints)
                elif cmd[1] == 'x':
                    try:
                        addr = int(cmd[2:].strip())
                    except (ValueError, TypeError):
                        self.clearbreakpoints(self.watchpoints)
                    else:
                        self.rmbreakpoint(addr, self.watchpoints)
                elif cmd[1] == 'f':
                    findstr = cmd[3:]
                    self.findstring(findstr.strip())
                elif cmd[1] == 'a':
                    args = map(int, cmdlist[1:])
                    self.asciidump(*args)
                elif cmd[1] == 'z':
                    arg = int(cmdlist[1])
                    print self.readstring(arg)
                elif cmd[1] == 'v':
                    fnroot = cmdlist[1]
                    self.mkresume(fnroot)
                elif cmd[1] == 'q':
                    print 'Bye!'
                    exit()
                else:
                    print 'Unrecognised debugger command'
                    print '  $l <address> - list'
                    print '  $s - step'
                    print '  $r - resume'
                    print '  $d - dump state to terminal'
                    print '  $m - memory dump to file'
                    print '  $b <addr> - add a breakpoint or list bps'
                    print '  $u <addr> - remove a breakpoint or clear bps'
                    print '  $w <addr> - add or list watchpoints'
                    print '  $x <addr> - remove or clear watchpoints'
                    print '  $f str - find \'str\' in memory'
                    print '  $a addr len - ASCII dump of memory at addr'
                    print '  $z addr - read string at addr'
                    print '  $v filenameroot - dump vm state to file'
                    print '  ($p addr - peek)'
                    print '  ($o addr val - poke)'
            else:
                try:
                    ret = eval(cmd)
                except (SyntaxError, NameError) as e:
                    print e
                else:
                    print ret
            if scriptline is not None:
                return

    def debugscript(self, script):
        for l in script.splitlines():
            print 'Executing \'{}\''.format(l)
            self.debug(l)
        
    def showbreakpoints(self, l):
        if l == self.breakpoints:
            pre = 'Break'
        else:
            pre = 'Watch'
        print pre + 'points at:',
        print ', '.join([str(x) for x in l])

    def addbreakpoint(self, addr, l):
        l.add(addr)
        if l == self.breakpoints:
            pre = 'Break'
        else:
            pre = 'Watch'
        print pre + 'point at {} added'.format(addr)

    def clearbreakpoints(self, l):
        l.clear()
        print 'Cleared'

    def readstring(self, addr, xor = 0):
        # read a length prefixed string at address
        length = self.memory[addr]
        return ''.join(map(chr, map(lambda x: x ^ xor, self.memory[addr + 1:addr + 1 + length])))

    def readlist(self, addr):
        # read a length prefixed list at address
        length = self.memory[addr]
        return self.memory[addr + 1:addr + 1 + length]

    def rmbreakpoint(self, addr, l):
        try:
            l.remove(addr)
            print 'Removed'
        except KeyError:
            print 'No break/watchpoint at {}'.format(addr)
            self.showbreakpoints(l)
        
    def memdump(self, fname = None):
        if fname is None:
            sys.stdout.write('filename: ')
            fname = sys.stdin.readline()
            fname = fname.strip()
        fd = open(fname, 'wb')
        fd.write(self.memory.data)
        fd.close
        print 'wrote memdump to {}'.format(fname)
        return

    def mkresume(self, fnroot):
        scriptfn = fnroot +  '.py'
        dumpfn = fnroot + '.bin'
        self.memdump(dumpfn)
        with open(scriptfn, 'w') as fd:
            fd.write('#!/usr/bin/env python2\n')
            fd.write('from vmlib import vm\n')
            fd.write('with open(\'{}\', \'r\') as fd:\n'.format(dumpfn))
            fd.write('    img = fd.read()\n')
            fd.write('resvm = vm.VM(img)\n')
            fd.write('resvm.stack = {}\n'.format(repr(self.stack)))
            fd.write('resvm.pc = {}\n'.format(repr(self.pc)))
            fd.write('resvm.registers = vm.wordarray({})\n'.format(repr(self.registers)))
            fd.write('resvm.breakpoints = {}\n'.format(repr(self.breakpoints)))
            fd.write('resvm.watchpoints = {}\n'.format(repr(self.watchpoints)))
            fd.write('resvm.inputbuffer = {}\n'.format(repr(self.inputbuffer)))
            fd.write('resvm.addbreakpoint(resvm.pc, resvm.breakpoints)\n')
            fd.write('resvm.run()\n')
    
    def value(self, x):
        if x < VM.MAXINT:
            return x
        elif self.isRegister(x):
            return self.registers[x - VM.MAXINT]
        else:
            raise VmInvalidValue('{} is not a valid value'.format(x))

    def findstring(self, s):
        locations = []
        ptr = 0
        while True:
            try:
                loc = self.memory.index(s, ptr)
                locations.append(loc)
                ptr = loc + 1
            except ValueError:
                break
        if len(locations) == 0:
            print repr(s) + ' not found'
        else:
            print 'found ' + repr(s) + ' at the following addresses:'
            for i in locations:
                print i
            print ''
            print '{} occurrences'.format(str(len(locations)))

    def asciidump(self, addr, count=64):
        for i in range(count):
            if i % 64 == 0:
                sys.stdout.write('\n')
                sys.stdout.write('{:7}: '.format(addr + i))
            try:
                char = chr(self.memory[addr + i])
            except ValueError:
                char = '?'
            sys.stdout.write(char)
        print
            
    def dump(self):
        print 'VM.dump()'
        print ''
        print 'pc={}, instructions={}'.format(self.pc,
                                                  self.instructionCount)
        print 'breakpoints: {}'.format(self.breakpoints)
        print 'watchpoints: {}'.format(self.watchpoints)
        print ''
        print 'stack: {}'.format(self.stack)
        print 'input buffer: \'{}\''.format(self.inputbuffer)
        for i, v in enumerate(self.registers):
            print '{}: {}'.format(self.regname(i), v)
        print ''

    def regname(self, i):
        if VM.useAlphaRegnames:
            return VM.RNAMES[i]
        else:
            return 'r{}'.format(i)

    def instr(self, address):
        opcode = self.memory[address]

        try:
            opname, nargs = VM.operators[opcode]
        except KeyError:
            raise VmBadOpcode('Bad Opcode {:d} at address {:d}'.format(opcode, address))

        args = self.memory[address+1:address+1+nargs]

        if args == 0:
            return opname

        for pos, arg  in enumerate(args):
            if self.isRegister(arg):
                args[pos] = self.regname(arg - VM.MAXINT)
            elif opname == 'out':
                try:
                    args[pos] = repr(chr(arg))
                except ValueError:
                    args[pos] = '??? ({})'.format(arg)
            else:
                args[pos] = str(arg)
                
        jump = 1 + nargs

        opstr = VM.opcodefmt.format(opname, ', '.join(args))
        
        return opstr , jump

    def listing(self, startaddress = 0, instructionCount=None):
        address = startaddress
        listing = []
        count = 0
        while address < VM.MEMSIZE:
            if instructionCount is not None:
                if count >= instructionCount:
                    break
            try:
                code, jump = self.instr(address)
            except VmBadOpcode:
                code, jump = '??? ({})'.format(self.memory[address]), 1
                if self.memory[address] < 256:
                    code = code + ' {}'.format(repr(chr(self.memory[address])))
                #break
            yield (address, code)
            #listing.append((address, code))
            count += 1
            address += jump
        #return listing

    def formattedListing(self, startaddress = 0, instructionCount = None):
        for addr, code in self.listing(startaddress, instructionCount):
            yield VM.addrfmt.format(addr, code)

    def formattedSubr(self, addr):
        RET = 18 # opcode for ret
        count = 1 # if addr contains ret, there's still one instruction
        offset = 0
        code, jump = self.instr(addr)
        while self.isMemory(addr + offset) \
          and self.memory[addr + offset] != RET:
            count += 1
            offset += jump
            code, jump = self.instr(addr + offset)
        return '\n'.join(l for l in self.formattedListing(addr, count))

    def isMemory(self, a):
        return a < VM.MAXINT

    def isRegister(self, a):
        return VM.MAXINT <= a < VM.MAXINT + VM.REGISTERS


    ##################################################################
    #
    # VM operations
    #
    ##################################################################
    # opcode 0
    def _halt(self):
        print 'stopping'
        fd = open('inputlog.txt', 'w')
        fd.write(self.inputlog)
        fd.close()
        raise VmStop('Program terminated by halt after {} steps'.format(self.instructionCount))

    # opcode 1
    def _set(self, a, b):
        val = self.value(b)
        self.store(a, val)

    # opcode 2
    def _push(self, a):
        self.stack.append(self.value(a))

    # opcode 3
    def _pop(self, a):
        result = self.stack.pop()
        self.store(a, result)

    # opcode 4
    def _eq(self, a, b, c):
        if self.value(b) == self.value(c):
            result = 1
        else:
            result = 0
        self.store(a, result)
            
    # opcode 5
    def _gt(self, a, b, c):
        if self.value(b) > self.value(c):
            result = 1
        else:
            result = 0
        self.store(a, result)

    # opcode 6
    def _jmp(self, a):
        address = self.value(a)
        self.pc = address

    # opcode 7
    def _jt(self, a, b):
        testValAddress = self.value(a)
        jumpAddress = self.value(b)
        if testValAddress != 0:
            self.pc = jumpAddress

    # opcode 8
    def _jf(self, a, b):
        testValAddress = self.value(a)
        jumpAddress = self.value(b)
        if testValAddress == 0:
            self.pc = jumpAddress

    # opcode 9
    def _add(self, a, b, c):
        result = (self.value(b) + self.value(c)) % VM.MAXINT
        self.store(a, result)

    # opcode 10
    def _mult(self, a, b, c):
        result = (self.value(b) * self.value(c)) % VM.MAXINT
        self.store(a, result)

    # opcode 11
    def _mod(self, a, b, c):
        result = self.value(b) % self.value(c)
        self.store(a, result)

    # opcode 12
    def _and(self, a, b, c):
        result = self.value(b) & self.value(c)
        self.store(a, result)
    
    # opcode 13
    def _or(self, a, b, c):
        result = self.value(b) | self.value(c)
        self.store(a, result)

    # opcode 14
    def _not(self, a, b):
        result = (~self.value(b))&VM.INTMASK
        self.store(a, result)

    # opcode 15
    def _rmem(self, a, b):
        addr = self.value(b)
        if addr in self.watchpoints:
            print 'Watchpoint at {} triggered by READ'.format(addr)
            self.debug()
        result = self.memory[addr]
        self.store(a, result)

    # opcode 16
    def _wmem(self, a, b):
        result = self.value(b)
        self.store(self.value(a), result)

    # opcode 17
    def _call(self, a):
        self._push(self.pc)
        self._jmp(a)

    # opcode 18
    def _ret(self):
        try:
            addr = self.stack.pop()
        except IndexError:
            self._halt()
        self._jmp(addr)

    # opcode 19
    def _out(self, a):
        char = self.value(a)
        sys.stdout.write(chr(char))
        sys.stdout.flush()

    # opcode 20
    def _in(self, a):
        if self.inputbuffer == '':
            sys.stdout.write('synacor> ')
            self.inputbuffer = sys.stdin.readline()
            self.inputlog += self.inputbuffer
        value = ord(self.inputbuffer[0])
        self.inputbuffer = self.inputbuffer[1:]
        self.store(a, value)

    # opcode 21
    def _noop(self):
        pass

if __name__ == '__main__':
    pass
