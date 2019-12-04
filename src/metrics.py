from __future__ import division
import math

import pandas as pd
import numpy as np


def calc_sensitivity(cause, actual, predicted):
    """Calculate sensitivity for a single cause

    Sensitivity is also known true positive rate, recall, or probability of
    detection. It is the number of correct predictions for the given cause
    over the total number of predictions for the cause:

    .. math::
        sensitivity = \\frac{TP}{P} = \\frac{TP}{TP + FN}

    where TP is the number of true postives prections, P is the number of true
    positives in the sample, and FN is the number of false positives
    predictions.

    Args:
        cause: a label in the actual and predicted series
        actual (pd.Series): true individual level classification
        predicted (pd.Series): individual level prediction

    Returns:
        float
    """
    true_positive = ((actual == cause) & (predicted == cause)).sum()
    n_predicted = (actual == cause).sum()
    return true_positive / n_predicted if n_predicted else np.nan


def calc_specificity(cause, actual, predicted):
    """Calculate specificity for a single cause

    Specificity is also know as the true negative rate. It is the number of
    prediction which are correctly determined to not be the given cause over
    the total number that to not belong to the cause

    .. math::
        specificity = \\frac{TN}{N} = \\frac{TN}{TN + FP}

    where TN is the number of true negatives predictions, N is the number of
    samples which are not the given cause, and FP is the number of false
    positive predictions.

    Args:
        cause: a label in the actual and predicted series
        actual (pd.Series): true individual level classification
        predicted (pd.Series): individual level prediction

    Returns:
        float
    """
    true_negative = ((actual != cause) & (predicted != cause)).sum()
    n_not_cause = (actual != cause).sum()
    return true_negative / n_not_cause if n_not_cause else np.nan


def calc_positive_predictive_value(cause, actual, predicted):
    """Calculate positive predictive value (PPV) for a single cause

    Positive predictive value is also known as precision. It is the number of
    correct predictions for a given cause over the total number of predictions
    of the cause:

    .. math::
         PPV = \\frac{TP}{PP} = \\frac{TP}{TP + FP}

    where TP is the number of true positive predictions, PP is the number of
    positive predictions, and FP is the number of false positive predictions.

    Args:
        cause: a label in the actual and predicted series
        actual (pd.Series): true individual level classification
        predicted (pd.Series): individual level prediction

    Returns:
        float
    """
    true_positive = ((actual == cause) & (predicted == cause)).sum()
    n_called = (predicted == cause).sum()
    return true_positive / n_called if n_called else np.nan


def calc_negative_predictive_value(cause, actual, predicted):
    """Calculate negative predictive value (NPV) for a single cause

    Negative predictive value is the number of prediction correctly determined
    to not belong to the given cause over the total number of predicted to
    not be the cause:

    .. math::
        NPV = \\frac{TN}{NP} = \\frac{TN}{TN + FP}

    where TN is the number of true negative predictions, NP is the number of
    negative predictions, and FP is the number of false positive predictions.

    Args:
        cause: a label in the actual and predicted series
        actual (pd.Series): true individual level classification
        predicted (pd.Series): individual level prediction

    Returns:
        float
    """
    true_negative = ((actual != cause) & (predicted != cause)).sum()
    n_not_predicted = (predicted != cause).sum()
    return true_negative / n_not_predicted if n_not_predicted else np.nan


def calc_specific_accuracy(cause, actual, predicted):
    """Calculate accuracy for a single cause

    Accuracy for a single cause is the number of predictions correctly
    classified with regard to this cause over the entire population.
    Misclassification of other labels among true negative predictions does
    not affect this statistic.

    .. math::
        accuracy = \\frac{TP + TN}{TP + FP + FN + TN}

    Args:
        cause: a label in the actual and predicted series
        actual (pd.Series): true individual level classification
        predicted (pd.Series): individual level prediction

    Returns:
        float
    """
    true_positive = ((actual == cause) & (predicted == cause)).sum()
    true_negative = ((actual != cause) & (predicted != cause)).sum()
    return (true_positive + true_negative) / len(actual)


def calc_overall_correctness(actual, predicted):
    """Calculate the proportion of correct individual-level predictions

    Args:
        actual (pd.Series): true individual level classification
        predicted (pd.Series): individual level prediction

    Return:
        float
    """
    return (actual == predicted).sum() / len(actual)


def calc_ccc(cause, actual, predicted):
    """Calculate chance-corrected concordance for a single cause

    Chance corrected metrics are derived from the general equation:

    .. math::

        K_j = \\frac{P(observed)_j - P(expected)_j}{1 - P(expected)_j}

    where K\ :sub:`J` is the corrected statistic for class j, P(observed)\
    :sub:`j` is the observed probability of j, and P(expected)\ :sub:`j` is
    the expected probability of j.

    Concordance is a multiclass generalization of sensitivity which captures
    number of observation on the diagonal of the misclassification matrix over
    the whole sample. This is corrected for chance by making the naive
    assumption that the likelihood of predicting a given cause purely by chance
    is uniformly distributed across cause. This differs from Cohen's kappa
    which assumes the likelihood of predicting a cause purely due to chance is
    a function of its true prevalences in the sample. The naive assumption
    gives estimates which are more comparable across study populations with
    different true underlying cause distributions and across studies which use
    different number of causes. For cause j, CCC is calculated as:

    .. math::
       CCC_j = \\frac{\\Big( \\frac{TP_j}{TP_j + FN_j}\\Big) - (\\frac{1}{N})}
               {1 - (\\frac{1}{N})}

    where TP is the true positive rate and FN is the false negative rate
    and N is the total number of observations.

    Args:
        cause: a label in the actual and predicted series
        actual (pd.Series): true individual level classification
        predicted (pd.Series): individual level predictions

    Returns:
        float
    """
    sensitivity = calc_sensitivity(cause, actual, predicted)
    chance = 1 / len(actual.unique())
    return (sensitivity - chance) / (1 - chance)


def agg_cause_specific_metrics(agg, metric, actual, predicted, weights=None):
    """Aggregate cause specific metrics into a single estimate

    It is useful to have a single performance metric at the individual-level.
    Some metrics only produce cause-specific estimates. These estimates can be
    aggregated in different ways to produce a single overall performance
    estimate.

    Args:
        agg (function): A function to aggregate across cause-specific estimates
            with the following sigature (sequence [, weights]) --> float where
            weights is a sequence with the same length as the number of actual
            prediction labels.
        metric (function): A function to compute cause specific metrics withthe
            following sigature: (label, pd.Series, pd.Series) --> float where
            label is a str or int value in the series.
        actual (pd.Series): true individual level classification
        predicted (pd.Series): individual level predictions
        weights (bool or sequence): use the true distribution as weights when
            aggregating across causes

    Returns:
        float

    Example:

    >>> agg_cause_specific_metrics(np.median, calc_ccc, actual, predicted)
    >>> agg_cause_specific_metrics(np.average, calc_ccc, actual, predicted,
                                   weights=True)
    """
    causes = actual.unique()
    if weights is True:
        csmf_true = (actual.value_counts() / len(actual)).loc[causes].values
        w = {'weights': csmf_true}
    elif weights:
        w = weights
    else:
        w = dict()
    return agg([metric(cause, actual, predicted) for cause in causes], **w)


def calc_mean_ccc(actual, predicted):
    """Calculate mean chance-corrected concordance across all causes

    Murray et al. recommend using the unweighted mean of the cause-specific
    chance-corrected concordance as an overall estimate of individual-level
    performance.

    Args:
        actual (pd.Series): true individual level classification
        predicted (pd.Series): individual level predictions

    Returns:
        float
    """
    return agg_cause_specific_metrics(calc_ccc, np.mean, actual, predicted)


def calc_median_ccc(actual, predicted):
    """Calculate median chance-corrected concordance across all causes

    Args:
        actual (pd.Series): true individual level classification
        predicted (pd.Series): individual level predictions

    Returns:
        float
    """
    return agg_cause_specific_metrics(calc_ccc, np.median, actual, predicted)


def calc_csmf_accuracy_from_csmf(actual, predicted):
    """Calculate Cause-Specific Mortality Fraction (CSMF) accuracy from CSMF
       estimates

    .. math::
       CSMF Accuracy = 1 - \\frac{\\sum_{j=1}^k |CSMF_j^{true}-CSMF_j^{pred}|}
                          {2 \\Big(1 - Minimum\\Big(CSMF_j^{true}\\Big)\\Big)}

    Args:
        actual (pd.Series): true population level CSMFs
        predicted (pd.Series): predicted population level CSMFs

    Returns:
        float
    """
    if not np.allclose(actual.sum(), predicted.sum(), 1):
        raise ValueError('CSMFs must sum to 1.')
    return 1 - (predicted - actual).abs().sum() / (2 * (1 - actual.min()))


def calc_csmf_accuracy(actual, predicted):
    """Calculate Cause-Specific Mortality Fraction (CSMF) accuracy from
       individual level predictions

    Args:
        actual (pd.Series): true individual level classification
        predicted (pd.Series): individual level predictions

    Returns:
        float
    """
    csmf_pred = pd.Series(predicted).value_counts(dropna=False) / len(actual)
    csmf_true = pd.Series(actual).value_counts(dropna=False) / len(actual)

    # Drop causes in the prediction which do not appear in the actual
    csmf_pred = csmf_pred.loc[csmf_true.index].fillna(0)
    return calc_csmf_accuracy_from_csmf(csmf_true, csmf_pred)


def correct_csmf_accuracy(uncorrected):
    """Correct Cause-Specific Mortality Fraction accuracy for chance

    Chance corrected metrics are derived from the general equation:

    .. math::

        K_j = \\frac{P(observed)_j - P(expected)_j}{1 - P(expected)_j}

    where K\ :sub:`j` is the corrected statistic for class j, P(observed)\
    :sub:`j` is the observed probability of j, and P(expected)\ :sub:`j` is
    the expected probability of j. It can be shown analytically and through
    simulation, that the expected CSMF accuracy tends towards 1 - e\ :sup:`-1`
    as the number of samples and classes tend towards infinity:

    .. math::

        \\lim_{N, j \\to \\infty} P(expected)_j = 1 - e^{-1}

    We use this approximation to correct CSMF accuracy for chance regardless
    of the number of samples or class:

    .. math::
        CCCSMF = \\frac{CSMF - (1 - e^{-1})}{1 - (1 - e^{-1})}
                 \\approx \\frac{CSMF - 0.632}{1 - 0.632}

    This provides a more interpretable metric in which 1.0 is perfect,
    0.0 is equivalent to chance and negative values are worst than chance.

    Args:
        uncorrected (float): Cause-Specific Mortality (CSMF) accuracy

    Returns:
        float
    """
    return (uncorrected - (1 - math.e**-1)) / (1 - (1 - math.e**-1))


def calc_cccsmf_accuracy(actual, predicted):
    """Calculate Chance-Corrected CSMF accuracy from individual level
       predictions

    Args:
        actual (pd.Series): true individual level classification
        predicted (pd.Series): individual level predictions

    Returns:
        float
    """
    return correct_csmf_accuracy(calc_csmf_accuracy(actual, predicted))


def calc_cccsmf_accuracy_from_csmf(actual, predicted):
    """Calculate Chance-Corrected Cause-Specific Mortality Fraction (CSMF)
       accuracy from CSMF estimates

    Args:
        actual (pd.Series): true population level CSMFs
        predicted (pd.Series): predicted population level CSMFs

    Returns:
        float
    """
    csmf = calc_csmf_accuracy_from_csmf(actual, predicted)
    return correct_csmf_accuracy(csmf)


def calc_median_and_ui(arr, n=500, random_state=None):
    """Calculate median and uncertain in median via bootstrapping.

    Args:
        arr: sequence of values to calculate statistics over
        n: number of bootstraps to perform

    Returns:
        tuple:
            * median (float)
            * uncertainty: tuple of floats, lower and upper bounds
    """
    if not random_state:
        random_state = np.random.RandomState()
    sampled = [np.median(random_state.choice(arr, len(arr)))
               for _ in range(500)]
    return np.median(arr), tuple(np.percentile(sampled, (2.5, 97.5)))
