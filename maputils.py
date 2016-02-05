#!/usr/bin/env python2
#
# utility classes for interpreting rooms, objects and constructing
# maps of the locations in the Synacor challenge
#
class room(object):
    def __init__(self, roomID = None, title = None,
                 description = None, exits = None,
                 subraddr = None, subr = None):
        self.roomID  = roomID # the address of the pointers fro this room
        self.title = title
        self.description = description
        if exits is None:
            self.exits = {}
        else:
            self.exits = exits
        self.subraddr = subraddr
        self.subr = subr

    def fromAddr(self, vm, addr):
        l = vm.memory[addr:addr+5]
        self.roomID = addr
        self.title = vm.readstring(l[0])
        descaddr = l[1]
        if vm.memory[descaddr] == 2:
            #two descriptions
            self.description = map(vm.readstring, vm.readlist(descaddr))
        else:
            self.description = [vm.readstring(l[1])]
        exitkeyaddr = l[2]
        exitvaladdr = l[3]
        exitkeyaddrs, exitvals = map(vm.readlist, l[2:4])
        exitkeys = map(vm.readstring, exitkeyaddrs)
        self.exits = zip(exitkeys, exitvals)
        self.subraddr = l[4]
        if self.subraddr == 0:
            self.subr = '<None>'
        else:
            self.subr = vm.formattedSubr(l[4])       
        
    def __str__(self):
        s = '## Room {} ##\n'.format(self.roomID)
        for i in self.description:
            s += '== {} ==\n\n{}\n\n'.format(self.title, i)
        s += 'Exits are\n'
        for name, target in self.exits:
            s += '- {} (Room {})\n'.format(name, target)
        s += '\nSubroutine @ {}'.format(self.subraddr)
        s += '\n' + self.subr + '\n'
        return s

class gameObject(object):
    def __init__(self):
        self.id = None
        self.name = None
        self.description = None
        self.location = None
        self.subraddr = None
        self.subr = None

    def fromAddr(self, vm, addr):
        self.id = addr
        self.name = vm.readstring(vm.memory[addr])
        self.description = vm.readstring(vm.memory[addr + 1])
        self.location = vm.memory[addr + 2]
        self.subraddr = vm.memory[addr + 3]
        if self.subraddr == 0:
            self.subr = '<None>'
        else:
            self.subr = vm.formattedSubr(self.subraddr)

    def __str__(self):
        s = '## Object {} ##\n'.format(self.id)
        s += '== {} ==\n\n{}\n\n'.format(self.name, self.description)
        s += 'Location: {}\n'.format(self.location)
        s += '\nSubroutine @ {}'.format(self.subraddr)
        s += '\n' + self.subr + '\n'
        return s

if __name__ == '__main__':
    # produce textual object/room list to stdout
    # create png images of room map with the dot and neato graphviz
    # renderers using pygraphviz
    from vmlib import vm
    import pygraphviz as pgv
    import re

    theMap = pgv.AGraph(directed=True)
    #
    # memdump1.bin is a dump of memory after the program has finished
    # the self-test and decryption phase
    #
    with open('memdump1.bin', 'r') as fd:
        image = fd.read()
    myvm = vm.VM(image)

    objlistaddr = 27381
    objlist = myvm.readlist(objlistaddr)
    objects = []
    for i in objlist:
        thisObj = gameObject()
        thisObj.fromAddr(myvm, i)
        objects.append(thisObj)
        print thisObj

    print '=' * 72
    
    raddr = 2317
    while raddr <= 2663:
        r = room()
        r.fromAddr(myvm, raddr)
        try:
            node = theMap.get_node(r.roomID)
            if r.title == 'Vault Lock':
                additional = re.search(r'(\'.+\')', r.description[0])
                if additional is not None:
                    r.title += ' ' + additional.group(1)
            node.attr['label'] = '({}) {}'.format(r.roomID, r.title)
        except KeyError:
            if r.title == 'Vault Lock':
                additional = re.search(r'(\'.+\')', r.description[0])
                if additional is not None:
                    r.title += ' ' + additional.group(1)
            theMap.add_node(r.roomID, label='({}) {}'.format(r.roomID, r.title))
        for d, t in r.exits:
            theMap.add_edge(r.roomID, t, label=d)
        print r
        objs = [i.name for i in objects if i.location == r.roomID]
        if len(objs) != 0:
            print '**Objects here:-'
            for i in objs:
                print '    {}'.format(i)
        print '-' * 72
        raddr += 5
        if raddr == 2462:
            raddr += 1

    theMap.write('room_map.dot')
    
    theMap.layout(prog='dot')
    theMap.draw('room_map_dot.png')

    theMap.layout(prog='neato')
    theMap.draw('room_map_neato.png')
    
