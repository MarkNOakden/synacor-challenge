#!/usr/bin/env python2
#import networkx as nx
import string

node_data = [ ['init',  '-',   9,    '*'],
              [   '+',    4, '-',     18],
              [     4,  '*',  11,    '*'],
              [   '*',    8, '-', 'test']]
    
def neighbours(r, c):
    if (r, c) == (0, 1):
        l = [(0, 2), (1, 1)]
    elif (r, c) == (1, 0):
        l = [(1, 1), (2, 0)]
    else:
        l = list( x for x in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
                if 0 <= x[0] <= 3 and 0 <= x[1] <= 3)
    return l

def coords_to_letter(r, c):
    return 'ABCDEFGHIJKLMNOP'[r*4 + c]

def letter_to_coords(l):
    tmp = 'ABCDEFGHIJKLMNOP'.index(l)
    return tmp / 4, tmp % 4

def get_weight(path):
    weight = 22
    calc = ['{}'.format(weight)]
    op = None
    for node in path:
        sym = vault_floor[node]
        if sym in ['+', '-', '*']:
            op = sym
            calc.append(op)
        else:
            weight = eval('{} {} {}'.format(weight, op, sym)) % 32768
            calc.append(str(sym))

    weight = eval('{} {} {}'.format(weight, op, 1))
    calc.append(str(1))
    
    return weight, ' '.join(calc)


# not required
#def reflect_AP(s):
#    return string.translate(s, string.maketrans('EIMJNO', 'BCDGHL'))
#
#def reflect_MD(s):
#    return string.translate(s, string.maketrans('IEFBC', 'NOKLH'))

# call as recurse('B', result_dict, 5)
def recurse(path_to_here, n_dict, result_dict, maxdepth):
    depth = len(path_to_here) #
    cur_node = path_to_here[-1]
    for i in n_dict[cur_node]:
        if depth == maxdepth:
            try:
                result_dict[i].append(path_to_here)
            except KeyError:
                result_dict[i] = [path_to_here]
        else:
            recurse(path_to_here + i, n_dict, result_dict, maxdepth)
                
if __name__ == '__main__':

    n_dict = {}
    vault_floor = {}
    
    for i, l in enumerate(node_data):
        for j, n in enumerate(l):
            if (i, j) != (0, 0) and (i, j) != (3, 3):
                vault_floor[coords_to_letter(i, j)] = n
                n_dict[coords_to_letter(i, j)] = []

    for i in range(4):
        for j in range(4):
            s = (i, j)
            if s in [(0, 0), (3, 3)]:
                continue
            for e in neighbours(*s):
                if e in [(0, 0), (3, 3)]:
                    continue
                n_dict[coords_to_letter(*s)].append(coords_to_letter(*e))

    # "algorithm"
    #
    # if we label the grid of rooms thus:-
    #
    # A B C D
    # E F G H
    # I J K L
    # M N O P
    #
    # Then the problem would seem to be to find a path of length 12
    # from A to P which may visit any node more than once except A
    # and P themselves.  The "orb weight" which starts at 22 at A
    # is modified at each step according to the values and operators
    # in node_data, (with 'init' being set weight to 22 and 'test'
    # being numeral "1" followed by a test fro equality with 30)
    #
    # The idea of this algorithm is to break up a path of length 12
    # from A to P as follows:
    # 1. generate all paths of length 6 from A to anywhere (not
    #    visiting A or P en-route)
    # 2. generate all paths of length 6 from P to anywhere (not
    #    visiting A or P en-route)
    # 3. for each path in [1] ending at a given node, join it to each
    #    path in [2] ending at the same node (Cartesian product over
    #    paths in [1] and [2] eding on a common node)
    #
    # Two refinements:
    #
    # A. To avoid hitting A or P, we can simply chop them off the grid
    #    and just look at paths of length 10 from B to L, B to O,
    #    E to L and E to O.
    #
    #    i.e. we use this grid:
    #
    #      B C D
    #    E F G H
    #    I J K L
    #    M N O
    #
    # B. Because of symmetry, we only have to work out the paths of
    #    depth 5 from B.  The other sets of paths are reflections of
    #    these in the two diagonals across the grid
    #
    # That said - the time taken to explicitly calculate the paths
    # of depth 5 from B is so small that we may as well repeat the
    # calculation for E, L and O
    #
    # Furthermore, the time taken to just calculate all depth 10 paths
    # and simply throw away those that don't end at L or O is equally
    # negligible

    # we store paths from B in a dict, indexed by the endpoint
    
    paths_from = {'B': {}, 'E': {}}

    recurse('B', n_dict, paths_from['B'], 10)
    recurse('E', n_dict, paths_from['E'], 10)

    #for i in paths_from_B.keys():
    #    print '{}: {}'.format(i, len(paths_from_B[i]))

    for start in 'BE':
        for end in 'OL':
            for p in paths_from[start][end]:
                s = p + end
                w, n = get_weight(s)
                if w == 30:
                    print s
                    print '{} = {}'.format(n, w)
    

