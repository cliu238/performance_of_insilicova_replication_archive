from __future__ import division

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import StratifiedShuffleSplit, LeavePGroupsOut
from sklearn.utils import resample, check_X_y
from sklearn.utils.validation import check_is_fitted

from prep import SITES
from metrics import (
    calc_ccc,
    calc_csmf_accuracy_from_csmf,
    correct_csmf_accuracy
)


class RandomClassifier(DummyClassifier):
    """Classifier to generate predictions uniformly at random

    This subclasses sklearn.dummy.DummyClassifier and overrides the predict
    method.
    """

    def __init__(self, random_state=None, **kwargs):
        self.strategy = 'uniform'
        self.constant = 1
        self.random_state = random_state
        for arg, val in kwargs.items():
            setattr(self, arg, val)

    def predict(self, X):
        """Perform classification on test X.

        This overrides the default behavior by of Sklearn classifiers by
        returning both individual and population level predictions. This is
        necessary because other classifiers estimate population distributions
        in a manner slightly de-coupled from individual predictions.

        Args:
            X (dataframe): samples by features to test

        Returns:
            tuple:
                * predictions (series): individual level prediction
                * csmf: (series): population level predictions
        """
        # This is a hack to use this classifer to test configuration where
        # the default setup is used. With the default, None, is passed to
        # ``clf.fit()`` and `clf.predict()`` doesn't know what classes to
        # predict.
        if not check_is_fitted(self, 'classes_'):
            self.fit(X, X.index)

        pred = super(RandomClassifier, self).predict(X)
        indiv = pd.Series(pred, index=X.index)
        csmf = indiv.value_counts() / len(indiv)
        return indiv, csmf


def prediction_accuracy(clf, X_train, y_train, X_test, y_test,
                        resample_test=True, resample_size=1):
    """Mesaure prediction accuracy of a classifier.

    Args:
        clf: sklearn-like classifier object. It must implement a fit method
            with the signature ``(X, y) --> self`` and a predict method with
            a signature ``(X) --> (y, csmf)``
        X_train (dataframe): samples by features matrix used for training
        y_train (series): target values used for training
        X_test (dataframe): samples by features matrix used for testing
        y_test (series): target values to compare predictions against
        resample_test (bool): resample test data to a dirichlet distribution
        resample_size (float): scalar applied to n of samples to determine
            output resample size.

    Returns:
        tuple:
            * preds (dataframe): two column dataframe with actual and predicted
                values for all observations
            * csmfs (dataframe): two column dataframe with actual and predicted
                cause-specific mortality fraction for each cause
            * trained (dataframe): matrix of learned associations between
                cause/symptom pairs from the training data
            * ccc (dataframe): chance-correct concordance for each cause in one row
            * accuracy (dataframe): summary accuracy measures in one row

    """
    y_pred, csmf_pred = clf.fit(X_train, y_train).predict(X_test)

    # All the outputs should be dataframes which can be concatentated and
    # saved without the index

    preds = pd.concat([y_test, y_pred], axis=1)
    preds.index.name = 'ID'
    preds.columns = ['actual', 'prediction']
    preds.reset_index(inplace=True)

    # Only calculate CCC for real causes. The classifier may predict causes
    # which are not in the set of true causes. This primarily occurs when
    # the classifier is run using default settings and no training or when it
    # isn't properly learning impossible causes.
    ccc = pd.DataFrame([{cause: calc_ccc(cause, y_test, y_pred)
                         for cause in y_test.unique()}])

    # It's possible for some classes predictions not to occur
    # These would result in missingness when aligning the csmf series
    csmf_actual = y_test.value_counts(dropna=False, normalize=True)
    csmf = pd.concat([csmf_actual, csmf_pred], axis=1).fillna(0)
    csmf.index.name = 'cause'
    csmf.columns = ['actual', 'prediction']
    csmf.reset_index(inplace=True)

    csmf_acc = calc_csmf_accuracy_from_csmf(csmf.actual, csmf.prediction)
    cccsmf_acc = correct_csmf_accuracy(csmf_acc)

    converged = int(clf.converged_) if hasattr(clf, 'converged_') else 1

    accuracy = pd.DataFrame([[
        ccc.iloc[0].mean(),
        ccc.iloc[0].median(),
        csmf_acc,
        cccsmf_acc,
        converged,
    ]], columns=['mean_ccc', 'median_ccc', 'csmf_accuracy', 'cccsmf_accuracy',
                 'converged'])

    return preds, csmf, ccc, accuracy


def dirichlet_resample(X, y, n_samples=None, random_state=None):
    """Resample so that the predicted classes follow a dirichlet distribution.

    When using a stratified split strategy for validation the cause
    distribution between the test and train splits are similiar. Resampling the
    test data using a dirichlet distribution provides a cause distribution in
    the test data which is uncorrelated to the cause distribution of the
    training data. This is essential for correctly estimating accuracy at
    the population level across a variety of population. A classifier which
    knows the output distribution may perform well by only predicting the most
    common causes regardless of the predictors. This classifier would easily
    do better than chance. Alternatively, a classifier may a very high
    sensitivity for only one cause and guess at random for all other causes.
    If only tested in a population with a high prevalence of this cause, the
    classifier may appear to be very good. Neither of these provide robust
    classifier which can be widely used. Resampling the test split provides a
    better estimate of out of sample validity. The dirichlet distribution is
    conjugate prior of the multinomial distribution and always sums to one, so
    it is suitable for resampling categorical data.

    Args:
        X (dataframe): samples by features matrix
        y (series): target values
        n_samples (int): number of samples in output. If none this defaults
            to the length of the input

    Return:
        tuple:
            * X_new (dataframe): resampled data
            * y_new (series): resampled predictions
    """
    if len(X.index.symmetric_difference(y.index)):
        raise ValueError('X and y do not have matching indices')
    check_X_y(X, y)

    if not n_samples:
        n_samples = len(X)

    causes = np.unique(y)
    n_causes = len(causes)

    # Draw samples from a dirichlet distribution where the alpha value for
    # each cause is the same
    csmf = np.random.dirichlet(np.ones(n_causes))

    # To calculate counts for each cause we multiply fractions through by the
    # desired sampled size and round down. We then add counts for the total
    # number of missing observations to achieve exactly the desired size.
    counts = np.vectorize(int)(csmf * n_samples)
    counts = counts + np.random.multinomial(n_samples - counts.sum(), csmf)

    X_new = pd.concat([resample(X.loc[y == cause], n_samples=counts[i])
                       for i, cause in enumerate(causes)])
    y_new = pd.Series(np.repeat(causes, counts), index=X_new.index)

    assert len(X_new) == len(y_new) == n_samples
    return X_new, y_new


def validate(X, y, clf, splits, subset=None, resample_test=True,
             resample_size=1, random_state=None):
    """Mesaure out of sample accuracy of a classifier.

    Args:
        X: (dataframe) rows are records, columns are features
        y: (series) predictions for each record
        clf: sklearn-like classifier object. It must implement a fit method
            with the signature ``(X, y) --> self`` and a predict method with
            a signature ``(X) --> (y, csmf)``
        model_selector: (sklearn model_selection) iterator to produce
            test-train splits with optional split_id method added
        groups: (series) encoded group labels for each sample
        ids: (dict) column -> constant, added to the returned dataframe
        subset: (tuple of int) splits to perform

    Returns:
        (tuple of dataframes): sames as ``prediction_accuracy`` for every split
            in ``subset`` with results concatenated.
    """
    output = [[], [], [], []]
    for i, (train_index, test_index, split_id) in enumerate(splits):
        if subset:
            start, stop = subset
            if i < start:
                continue
            if i > stop:
                break

        if train_index is None:
            X_train = None
            y_train = None
        else:
            X_train = X.iloc[train_index]
            y_train = y.iloc[train_index]

        X_test = X.iloc[test_index]
        y_test = y.iloc[test_index]

        if resample_test:
            n_samples = round(resample_size * len(X_test))
            X_test, y_test = dirichlet_resample(X_test, y_test, n_samples)

        results = prediction_accuracy(clf, X_train, y_train, X_test, y_test)

        for i, result in enumerate(results):
            result['split'] = split_id
            output[i].append(result)

    return list(map(pd.concat, output))


def out_of_sample_splits(X, y, n_splits, test_size=.25, random_state=None):
    splits = StratifiedShuffleSplit(n_splits=n_splits, test_size=test_size,
                                    random_state=random_state).split(X, y)
    for i, (train, test) in enumerate(splits):
        yield train, test, i


def in_sample_splits(X, y, n_splits):
    X, y = check_X_y(X, y)
    idx = np.arange(len(y))
    for i in range(n_splits):
        yield idx, idx, i


def no_training_splits(X, y, n_splits):
    X, y = check_X_y(X, y)
    idx = np.arange(len(y))
    for i in range(n_splits):
        yield None, idx, i
