import numpy as np
import pandas as pd
import pytest
import rpy2.robjects
import rpy2.robjects.packages

from insilico import InsilicoClassifier


class TestGettters(object):
    def test_returns_rpy2_converted_package(self):
        clf = InsilicoClassifier()
        pkg = clf.get_r_insilico_package()
        assert isinstance(pkg, rpy2.robjects.packages.InstalledSTPackage)
        assert 'insilico_fit' in pkg._exported_names
        assert isinstance(pkg.insilico_fit,
                          rpy2.robjects.functions.DocumentedSTFunction)
        assert 'extract_prob' in pkg._exported_names
        assert isinstance(pkg.extract_prob,
                          rpy2.robjects.functions.DocumentedSTFunction)

    def test_get_sample_data(self):
        clf = InsilicoClassifier()
        df = clf.get_sample_data()
        assert isinstance(df, pd.DataFrame)

    def test_get_cond_prob_num(self):
        clf = InsilicoClassifier()
        df = clf.get_cond_prob_num()
        assert isinstance(df, pd.DataFrame)

    def test_get_causes(self):
        clf = InsilicoClassifier()
        causes = clf.get_insilico_causes()
        assert isinstance(causes, list)

    def test_get_symptoms(self):
        clf = InsilicoClassifier()
        symptoms = clf.get_insilico_symptoms()
        assert isinstance(symptoms, list)

    def test_get_short_cause_map(self):
        clf = InsilicoClassifier()
        cause_map = clf.get_insilico_short_causes()
        assert isinstance(cause_map, dict)


@pytest.fixture(scope='module', params=[
    ('data', np.tile(np.eye(5), (4, 1))),
    ('data', pd.DataFrame(np.tile(np.eye(5), (4, 1)))
               .replace({1: 'Y', 0: ''}).values),
    ('index', np.arange(20)),
    ('index', np.arange(40, 60)),
    ('index', np.repeat(np.arange(4), 5)),
    ('columns', np.arange(5)),
    ('columns', np.arange(5, 10)),
    ('data', np.ones((20, 5))),
    ('data', np.zeros((20, 5))),
    ('data', np.concatenate([np.eye(5) for i in range(4)])),
])
def extracted_data(request):
    clf = InsilicoClassifier()

    key, value = request.param
    df_data = {
        'data': np.concatenate([np.eye(5) for i in range(4)]),
        'index': ['row{}'.format(i) for i in range(20)],
        'columns': ['col{}'.format(i) for i in range(5)],
    }

    if key == 'gs':
        y = pd.Series(value)
    else:
        y = pd.Series(['gold{}'.format(x) for x in np.repeat(np.arange(5), 4)])
        df_data.update({key: value})

    df = pd.DataFrame(**df_data)
    y.index = df.index

    probs = clf.extract_prob(df, y)
    return probs, df, y


class TestExtractProb(object):
    def test_returns_namedtuple(self, extracted_data):
        probs, df, y = extracted_data
        assert isinstance(probs, tuple)

    def test_returns_cond_prob_dataframe(self, extracted_data):
        probs, df, y = extracted_data
        assert isinstance(probs.cond_prob, pd.DataFrame)

    def test_cond_prob_index_match_input_columns(self, extracted_data):
        probs, df, y = extracted_data
        assert set(probs.cond_prob.index).issubset(df.columns)

    def test_cond_prob_columns_match_input_gs(self, extracted_data):
        probs, df, y = extracted_data
        assert not set(probs.cond_prob.columns).symmetric_difference(y)

    def test_cond_prob_values_between_zero_and_one(self, extracted_data):
        probs, df, y = extracted_data
        assert ((probs.cond_prob >= 0) & (probs.cond_prob <= 1)).all().all()

    def test_returns_cond_prob_alpha_dataframe(self, extracted_data):
        probs, df, y = extracted_data
        assert isinstance(probs.cond_prob_alpha, pd.DataFrame)

    def test_cond_prob_alpha_index_match_input_columns(self, extracted_data):
        probs, df, y = extracted_data
        assert set(probs.cond_prob_alpha.index).issubset(df.columns)

    def test_cond_prob_alpha_columns_match_input_gs(self, extracted_data):
        probs, df, y = extracted_data
        assert not set(probs.cond_prob_alpha.columns).symmetric_difference(y)

    def test_returns_table_alpha_array(self, extracted_data):
        probs, df, y = extracted_data
        assert isinstance(probs.table_alpha, np.ndarray)

    def test_returns_table_num_array(self, extracted_data):
        probs, df, y = extracted_data
        assert isinstance(probs.table_num, np.ndarray)

    def test_table_num_values_between_zero_and_one(self, extracted_data):
        probs, df, y = extracted_data
        assert np.all(probs.table_num >= 0) & np.all(probs.table_num <= 1)

    def test_returns_symp_train_dataframe(self, extracted_data):
        probs, df, y = extracted_data
        assert isinstance(probs.symps_train, pd.DataFrame)

    def test_symps_train_index_matches_inputs(self, extracted_data):
        probs, df, y = extracted_data
        assert np.all(probs.symps_train.index == df.index)

    def test_symps_train_columns_match_inputs(self, extracted_data):
        probs, df, y = extracted_data
        assert set(probs.symps_train.columns).issubset(df.columns)

    def test_symps_train_values_match_inputs(self, extracted_data):
        probs, df, y = extracted_data
        assert (probs.symps_train == df[probs.symps_train.columns]).all().all()

    def test_same_predictors_used(self, extracted_data):
        probs, df, y = extracted_data
        assert set(probs.symps_train.columns) == set(probs.cond_prob.index)
        assert np.all(probs.cond_prob.index == probs.cond_prob_alpha.index)


@pytest.mark.parametrize("thre", np.arange(0.15, 1, .1))
def test_missingness_threshold(thre):
    clf = InsilicoClassifier()

    # Create a dataframe which looks like a checker board of 1s and 0s
    # and set the first n percent of the observations in the column to missing.
    # The percent missing is the column header
    df = pd.DataFrame(np.tile([1, 0], 550).reshape((100, 11)),
                      index=['I{}'.format(i) for i in range(100)],
                      columns=['{}0%'.format(i) for i in range(11)])
    for x in range(11):
        df.iloc[np.arange(0, x * 10), x] = -1

    # The pattern of five letters repeat over and over. This ensures that the
    # for each y value some are missing others are not.
    y = pd.Series(np.tile(['a', 'b', 'c', 'd', 'e'], 20), index=df.index)
    clf.extract_prob(df, y, missingness_threshold=thre)
    df.iloc[:, np.arange(int((thre + 0.05) * 10))].columns


@pytest.fixture
def default_fit_params():
    return {
        'Nsim': 5,
        'burnin': 2,
        'auto_length': False,
        'external_sep': False,
    }


@pytest.fixture(scope='module')
def fit_data():
    """Small data set with one injury observation"""
    clf = InsilicoClassifier()
    df = clf.get_sample_data().iloc[np.arange(30, 40)]
    fit = clf.insilico_fit(df, n_sim=1000, burn_in=100, auto_length=False)
    return df, fit


class TestInsilicoFit(object):

    def test_returns_tuple(self, fit_data):
        df, fit = fit_data
        assert isinstance(fit_data, tuple)

    def test_returns_sid_array(self, fit_data):
        df, fit = fit_data
        assert isinstance(fit.sid, np.ndarray)

    def test_output_sids_match_inputs(self, fit_data):
        df, fit = fit_data
        assert not any(df.index.symmetric_difference(fit.sid))

    def test_returns_data_dataframe(self, fit_data):
        df, fit = fit_data
        assert isinstance(fit.data, pd.DataFrame)

    def test_output_data_columns_match_inputs(self, fit_data):
        """
        Insilico doesn't store dimnames on the output data matrix so the
        columns will be labeled based on their position and prefixed with on
        'X'. These won't match the input column names.
        """
        df, fit = fit_data
        assert fit.data.columns.symmetric_difference(df.columns).any()

    def test_returns_indiv_probs_dataframe(self, fit_data):
        df, fit = fit_data
        assert isinstance(fit.indiv_prob, pd.DataFrame)


@pytest.mark.parametrize("labels,encoded", [
    (['foo', 'Bar'], ['foo', 'Bar']),
    (['foo bar'], ['foo.bar']),
    (['foo (bar)', 'blah-blah'], ['foo..bar.', 'blah.blah']),
    (['foo bar', 2], ['foo.bar', '.']),
])
def test_get_labels_map(labels, encoded):
    clf = InsilicoClassifier()
    expected = dict(zip(encoded, labels))
    observed = clf.get_labels_map(labels)
    assert expected == observed


class TestMostProbable(object):

    @pytest.mark.parametrize("values,index,biggest", [
        ([0, 1, 2], ['a', 'b', 'c'], 'c'),
        ([2, 1, 0], ['a', 'b', 'c'], 'a'),
        ([0, 1, 0], ['a', 'b', 'c'], 'b'),
        ([-2, -1, 0], ['a', 'b', 'c'], 'c'),
    ])
    def test_returns_biggest(self, values, index, biggest):
        clf = InsilicoClassifier()
        s = pd.Series(values, index=index)
        b = clf.indiv_most_probable(s)
        assert b == biggest

    @pytest.mark.parametrize("values,index,biggest", [
        ([0, 1, 1], ['a', 'b', 'c'], ['b', 'c']),
        ([1, 0, 1], ['a', 'b', 'c'], ['a', 'c']),
        ([1, 1, 0], ['a', 'b', 'c'], ['a', 'b']),
    ])
    def test_tie_for_biggest(self, values, index, biggest):
        clf = InsilicoClassifier()
        s = pd.Series(values, index=index)
        b = clf.indiv_most_probable(s)
        assert b in biggest

    @pytest.mark.parametrize("values", [
        [0, 0, 0],
        [1, 1, 1],
        [2, 2, 2],
    ])
    def test_all_tied(self, values):
        clf = InsilicoClassifier()
        s = pd.Series(values, index=['a', 'b', 'c'])
        b = clf.indiv_most_probable(s)
        assert b == 'Undetermined'
