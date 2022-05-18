import sys; sys.path.append("..")

from utils import random_vector, random_equivalent
import binvec
from bidict import bidict

def test_renaming():
    '''
        checks whether the binvec.binvec.rename-function works as expected.
    '''
    u = binvec.vec({ "x": 0, "y": 1, "z": 0 })
    uprime = u.rename(bidict({ "x": "z", "y": "y", "z": "x" }))
    assert u == uprime 
    uprime = u.rename(bidict({ "x": "y", "y": "z", "z": "x" }))
    expected_result = binvec.vec({ "x": 0, "y": 0, "z": 1 })
    assert uprime == expected_result

def test_h_g_switch():
    '''
        checks whether the self-inversion property of the switching function holds.

        hash: tLQ9uGaAlU
    '''
    H = [ "x0", "x1", "x2" ]
    for _ in range(100):
        # create random vector, renaming and flip-set
        pi, S = random_equivalent(H, var_pref="y")
        u = random_vector(set(H) | set(pi.values()))
        # check if applying the switch twice results in the original vector again
        uprime = u.apply_switch(pi, S)
        uprimeprime = uprime.apply_switch(pi, S)
        assert uprimeprime == u


