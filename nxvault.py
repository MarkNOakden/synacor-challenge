#!/usr/bin/env python2
import networkx as nx

node_data = [ ['init',  '-',   9,    '*'],
              [   '+',    4, '-',     18],
              [     4,  '*',  11,    '*'],
              [   '*',    8, '-', 'test']]

def neighbours(r, c):
    l = list( x for x in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
              if 0 <= x[0] <= 3 and 0 <= x[1] <= 3)
    return l

def allpaths(G, now, target, retpath, depth):
    if retpath is None: retpath = []
    if depth == 12:
        if now == target:
            yield retpath
        else:
            yield None
    else:
        for i in neighbours(*now):
            retpath += i
            yield allpaths(G, i, target, retpath, depth - 1)

if __name__ == '__main__':
    graph = nx.Graph()
    for i, l in enumerate(node_data):
        for j, n in enumerate(l):
            graph.add_node((i,j), label=n)

    #print graph.nodes(data=True)

    for i in range(4):
        for j in range(4):
            s = (i, j)
            #print s, ':', neighbours(*s)
            for e in neighbours(*s):
                graph.add_edge(s, e)

    import matplotlib.pyplot as plt

    nx.draw_graphviz(graph)
    plt.savefig('vault.png')

    #paths = nx.all_simple_paths(graph, (0,0), (3,3))
    #print list(paths)
    for p in allpaths(graph, (0,0), (3,3), None, 13):
        print p
        op = None
        weight = 22
        for node in p:
            n = graph.node[node]['label']
            if n in ['+', '-', '*']:
                op = n
            elif n == 'init':
                weight = 22
            elif n == 'test':
                n = 1
                weight = eval('{} {} {}'.format(weight, op, n)) % 32768
            else:
                weight =  eval('{} {} {}'.format(weight, op, n)) % 32768
            print graph.node[node]['label'],
            while weight < 0:
                weight = weight + 32768
            print '=',weight,
            if weight == 30:
                print '<----- !!!***'
            else:
                print

# pseudocode
#
# depth = 0
# now = 0,0 ; target = 3,3
# path(now, target, depth)
#   PATH = None
#   if depth == 12:
#     if now == target:
#       yield path
#     else:
#       yield None
#    else:
#      for i in neighbours(now):
#        yield path(i, target, depth - 1)#
    
#
# 
            

    
