from __future__ import division

import pytest
import numpy as np
import pandas as pd
import math

from validation import *


@pytest.fixture
def xyg():
    x = pd.DataFrame(np.zeros((100, 5)))
    y = pd.Series(np.tile(np.arange(5), 20))
    g = pd.Series(np.array([math.floor(i / 20) for i in range(100)]))
    return x, y, g


class TestOutOfSampleAccuracy(object):

    def test_selector_StratifiedShuffleSplit(self, xyg):
        x, y, g = xyg
        n_splits = 7
        ms = out_of_sample_splits(x, y, n_splits)
        clf = RandomClassifier()
        validate(x, y, clf, ms)

    def test_selector_StratifiedShuffleSplit_splits(self, xyg):
        x, y, g = xyg
        n_splits = 5
        ms = out_of_sample_splits(x, y, n_splits)
        clf = RandomClassifier()
        results = validate(x, y, clf, ms)
        preds, csmf, ccc, accuracy = results
        assert len(accuracy) == n_splits


class TestStratifiedShuffleSplit(object):

    def test_seed(self):
        X = np.arange(500).reshape((100, 5))
        y = np.repeat(np.arange(10), 10)
        seed = 8675309
        splits1 = list(out_of_sample_splits(X, y, n_splits=10,
                                            random_state=seed))
        splits2 = list(out_of_sample_splits(X, y, n_splits=10,
                                            random_state=seed))

        assert all([(splits1[i][0] == splits2[i][0]).all() and
                    (splits1[i][1] == splits2[i][1]).all()
                    for i in range(len(splits1))])
