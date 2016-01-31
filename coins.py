#!/usr/bin/env python2
import itertools

coins = [2, 3, 5, 7, 9]

def tot(comb):
	return comb[0] + comb[1] * comb[2]**2 + comb[3]**3 - comb[4]

for i in itertools.permutations(coins, 5):
    x = tot(i)
    if x == 399:
        print i, x
    
