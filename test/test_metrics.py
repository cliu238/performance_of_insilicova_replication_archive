import pandas as pd
import pytest

from metrics import *


class TestCalcCCC(object):
    def test_perfect_prediction(self):
        """4 of 4 correct"""
        i = ['a', 'b', 'c', 'd']
        a = pd.Series([1, 2, 1, 2], index=i)
        p = pd.Series([1, 2, 1, 2], index=i)
        ccc = calc_ccc(1, a, p)
        assert ccc == 1

    def test_at_chance(self):
        """2 possibilities and 50% (2 of 4)correct"""
        i = ['a', 'b', 'c', 'd']
        a = pd.Series([1, 2, 1, 2], index=i)
        p = pd.Series([1, 1, 2, 2], index=i)
        ccc = calc_ccc(1, a, p)
        assert ccc == 0

    def test_all_wrong(self):
        """0 of 4 correct"""
        i = ['a', 'b', 'c', 'd']
        a = pd.Series([1, 2, 1, 2], index=i)
        p = pd.Series([2, 1, 2, 1], index=i)
        ccc = calc_ccc(1, a, p)
        assert ccc == -1


class TestCCCSMFAccuracy(object):
    def test_perfect_prediction(self):
        """All correct"""
        i = ['a', 'b', 'c', 'd']
        a = pd.Series([.5, .2, .2, .1], index=i)
        p = pd.Series([.5, .2, .2, .1], index=i)
        csmf_acc = calc_csmf_accuracy_from_csmf(a, p)
        assert csmf_acc == 1
