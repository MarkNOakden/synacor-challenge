#!/usr/bin/env python2

# real problem has BITS=15
BITS = 15
MOD = 1 << BITS

print 'maths modulo', MOD

def trace(f):
    trace.depth = 0
    def _f(*args, **kwargs):
        print "  " * trace.depth, ">", f.__name__, args, kwargs
        trace.depth += 1
        res = f(*args, **kwargs)
        trace.depth -= 1
        print "  " * trace.depth, "<", res
        return res
    return _f

#@trace
def fn(A, B):
    global memo, calls, hits
    calls += 1
    key = (A,B)
    if key in memo.keys():
        hits += 1
        return memo[key]
    if A == 0:
        ret = (B + 1) % MOD # I think this os the only place that
                          # anything can overflow BITS
        memo[key] = ret
        return ret
    elif A == 1:
        ret = (H + 1 + B) % 32768
        memo[key] = ret
        return ret
    elif A == 2:
        ret = (H * (B + 2) + B + 1) % 32768
        memo[key] = ret
        return ret
    elif B == 0:
        ret = fn(A - 1, H)
        memo[key] = ret
        return ret
    ret = fn(A - 1, fn(A, B - 1))
    memo[key] = ret
    return ret

# Real problem is A=4, B=1, find H such that fn(A,B) = (6, <anything))
# smaller values for A don't break python recursion, but A=4 causes
# a "Maximum recursion depth exceeded" exception

# 
A = 4 % MOD
B = 1 % MOD

try:
    for H in xrange(3):
        memo = {}
        calls = 0
        hits = 0
        print H, fn(A, B), calls, hits
except RuntimeError:
    # lets save the memoised return values so we can look for patterns
    with open('memo.txt', 'w') as fd:
        fd.write(repr(memo))
    raise

