#!/usr/bin/env python2

nodes = [ ['init',  '-',   9,    '*'],
          [   '+',    4, '-',     18],
          [     4,  '*',  11,    '*'],
          [   '*',    8, '-', 'test']]

graph = {}

def neighbours(r, c):
    l = list( x for x in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
              if 0 <= x[0] <= 3 and 0 <= x[1] <= 3)
    return l

def paths(graph, start, end, subpath=None):
    if subpath is None:
        subpath = []

    subpath.append(start)

    if start == end:
        return subpath

    if not graph.has_key(start):
        return None

    for node in graph[start]:
        if node not in subpath:
            newpath = paths(graph, node, end, subpath)
            if newpath:
                return newpath

    return None

for i, l in enumerate(nodes):
    for j, n in enumerate(l):
        graph[(i,j)] = neighbours(i, j)

print graph

print paths(graph, (0,0), (3,3))

for (i, j) in paths(graph, (0,0), (3,3)):
    print nodes[i][j],
print ''


