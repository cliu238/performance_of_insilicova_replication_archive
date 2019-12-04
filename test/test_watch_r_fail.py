import contextlib
import itertools

import numpy as np
from rpy2.robjects import pandas2ri
from rpy2.rinterface import RRuntimeError
from rpy2.robjects.packages import importr
import pytest

from insilico import InsilicoClassifier


AGES = ['elder', 'midage', 'adult', 'child', 'under5', 'infant', 'neonate']
SEXES = ['male', 'female']
INJURIES = ['injury', 'traffic', 'o_trans', 'fall', 'drown', 'fire', 'assault',
            'venom', 'force', 'poison', 'inflict', 'suicide']


@contextlib.contextmanager
def pandas2ri_activated():
    pandas2ri.activate()
    try:
        yield
    finally:
        pandas2ri.deactivate()


@contextlib.contextmanager
def not_raises():
    """See: https://github.com/pytest-dev/pytest/issues/1830"""
    try:
        yield
    finally:
        pass


@pytest.fixture
def df():
    clf = InsilicoClassifier()
    df = clf.get_sample_data().reset_index()
    df = df.set_index(df.columns[0], drop=False)

    gs_list = ['A', 'B', 'C', 'D', 'E']
    gs_name = 'GS'
    gs = np.repeat(gs_list, df.shape[0] / len(gs_list))
    df[gs_name] = gs

    return df


@pytest.fixture
def params():
    return {
        'auto_length': False,
        'Nsim': 10,
        'burnin': 1,
    }


@pytest.mark.parametrize('learning_type, context', [
    (None, not_raises()),
    ('quantile', not_raises()),
    ('foobar', pytest.raises(RRuntimeError)),
])
def test_train_with_wrong_learning_type(df, learning_type, context):
    clf = InsilicoClassifier()
    gs_list = list(df['GS'].unique())

    learning = {'type': learning_type} if learning_type else dict()

    with pandas2ri_activated():
        with context:
            clf.r_insilico.extract_prob(df, 'GS', gs_list, **learning)


@pytest.mark.parametrize('thre, context', [
    (-7, pytest.raises(RRuntimeError)),
    (0, pytest.raises(RRuntimeError)),
    (0.5, not_raises()),
    (1, not_raises()),
    (2.5, not_raises()),
])
def test_train_drop_all_missing(df, thre, context):
    """
    The threshold for misisngness ``thre`` can be any number. It is interpreted
    as a proportion, so ideally it should be between zero and one. A threshold
    of zero or less indicates that the user only wishes to use columns which
    have no missingness. A threshold of one or more indicates that the user
    wishes to keep all columns from the training data regardless of the
    amount of missingness.

    With a zero or negative missingness threshold (i.e. no missingess allowed)
    and some missingness in all columns, R will drop all columns and attempt to
    subset an empty data structure.
    """
    clf = InsilicoClassifier()
    gs_list = list(df['GS'].unique())

    # Set the first row to all missing except the ID
    df.iloc[0, 1:] = '.'

    with pandas2ri_activated():
        with context:
            clf.r_insilico.extract_prob(df, 'GS', gs_list, thre=thre)


@pytest.mark.parametrize('thre, context', [
    (0.999, pytest.raises(RRuntimeError)),
    (1, not_raises()),
])
def test_train_drops_all_but_one_missing(df, thre, context):
    """
    Siminarily to above, if only one column is above the missingness threshold,
    all but one columns are dropped. This results in a one dimensional data
    structure. When R attempts to subset in two dimensions it throws an error.
    """
    clf = InsilicoClassifier()
    gs_list = list(df['GS'].unique())

    # Set all values in all columns except the ID and first column to missing
    df.iloc[:, 2:] = '.'

    with pandas2ri_activated():
        with context:
            clf.r_insilico.extract_prob(df, 'GS', gs_list, thre=thre)


@pytest.mark.parametrize('val, context', [
    ('Y', not_raises()),
    ('', not_raises()),
    ('.', pytest.raises(RRuntimeError)),
])
def test_train_all_one_value(df, val, context):
    clf = InsilicoClassifier()
    gs_list = list(df['GS'].unique())

    df.loc[:, :] = val

    with pandas2ri_activated():
        with context:
            clf.r_insilico.extract_prob(df, 'GS', gs_list, thre=0)


def test_train_gs_col_not_found(df):
    clf = InsilicoClassifier()
    gs_list = list(df['GS'].unique())

    with pandas2ri_activated():
        with pytest.raises(RRuntimeError):
            clf.r_insilico.extract_prob(df, 'foo', gs_list)


@pytest.mark.parametrize('mask, context', [
    ([], not_raises()),
    (AGES, pytest.raises(RRuntimeError)),
    (SEXES, pytest.raises(RRuntimeError)),
])
def test_no_demographics(df, params, mask, context):
    clf = InsilicoClassifier()

    df.loc[:, mask] = ''

    with pandas2ri_activated():
        with context:
            clf.r_insilico.insilico(df.drop('GS', axis=1), **params)


@pytest.mark.parametrize('mask, context', [
    ([], not_raises()),
    (INJURIES, pytest.raises(RRuntimeError)),
])
def test_predict_with_no_injuries(df, params, mask, context):
    clf = InsilicoClassifier()

    df = df.drop('GS', axis=1)
    df.loc[:, mask] = ''

    with pandas2ri_activated():
        with context:
            clf.r_insilico.insilico(df, **params)


@pytest.mark.parametrize('mask, context', [
    ([], not_raises()),
    (INJURIES, pytest.raises(RRuntimeError)),
])
def test_predict_with_all_injuries(df, params, mask, context):
    clf = InsilicoClassifier()

    df = df.drop('GS', axis=1)
    df.loc[:, mask] = 'Y'

    with pandas2ri_activated():
        with context:
            clf.r_insilico.insilico(df, **params)


def test_predict_with_burnin_gt_nsim(df):
    clf = InsilicoClassifier()

    with pandas2ri_activated():
        with pytest.raises(RRuntimeError):
            clf.r_insilico.insilico(df, burnin=50, Nsim=10)


def test_predict_with_thin_gt_nsim():
    clf = InsilicoClassifier()

    with pandas2ri_activated():
        with pytest.raises(RRuntimeError):
            clf.r_insilico.insilico(df, thin=50, Nsim=10)


@pytest.mark.parametrize('mask, context', [
    ([], not_raises()),
    (AGES + SEXES, pytest.raises(RRuntimeError)),
])
def test_predict_with_training_but_no_impossible_causes(df, params, mask, context):
    clf = InsilicoClassifier()
    rbase = importr('base')
    symptoms = clf.get_insilico_symptoms()
    causes = clf.get_insilico_causes()

    test = df.drop('GS', axis=1)
    train = df.copy()
    cause_cycle = itertools.cycle(causes)
    train['GS'] = [next(cause_cycle) for i in df.index]

    with pandas2ri_activated():
        probs = clf.r_insilico.extract_prob(train, 'GS', causes,
                                            type='empirical')
        cond_prob = pandas2ri.ri2py(rbase.data_frame(probs.rx2('cond.prob')))
        cond_prob = cond_prob.loc[symptoms, causes].fillna(0)
        cond_prob.loc[mask] = .5  # all non-zero (no impossible combos)
        with context:
            clf.r_insilico.insilico(test, CondProbNum=cond_prob.values,
                                    **params)


def test_predict_with_numeric_encoding(df, params):
    clf = InsilicoClassifier()

    df = df.replace({'Y': 1, '': 0, '.': -1})

    with pandas2ri_activated():
        with pytest.raises(RRuntimeError):
            clf.r_insilico.insilico(df, isNumeric=True, **params)
