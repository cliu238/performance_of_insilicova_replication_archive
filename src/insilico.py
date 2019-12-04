from collections import namedtuple
import re
from warnings import warn

import numpy as np
from rpy2 import robjects
from rpy2.rinterface import RNULLType
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
from rpy2.robjects.pandas2ri import ri2py


class InsilicoClassifier(object):
    """Implement the InSilicoVA algorithm for classifying verbal autopsies.

    This classifier is loosely based off of sklearn classifiers. Parameters
    used to initialize the classifier are model hyperparameters which affect
    the fitting and prediction. These all have a default value of ``None``.
    Values which are not explicitly set are removed before calling the
    corresponding R function. This allows the R function to use it's defaults
    without verfying that the defaults match.

    Attributes with trailing underscores are parameters derived from the
    training data and are used to predict. These are stored on the classifier
    after calling the ``fit`` method.

    Args:
        symptoms (sequence of strings): names of column labels to use. If the
            input data contains additional columns, these will be dropped. If
            the input data is missing any of these columns, these will be
            ignored.
        update_cond_prob (bool): see ``updateCondProb`` on the ``insilico`` R
            function
        keep_prob_base_level (bool): see ``keepProbbase.level`` on the
            ``insilico`` R function
        external_sep (bool): see ``external.sep`` on the ``insilico`` R
            function
        n_sim (int): see ``Nsim`` on the ``insilico`` R function
        thin (int): see ``thin`` on the ``insilico`` R function
        burn_in (int): see ``burnin`` on the ``insilico`` R function
        auto_length (bool): see ``auto.length`` on the ``insilico`` R function
        conv_csmf (float): see ``conv.csmf`` on the ``insilico`` R function
        jump_scale (float): see ``jump.scale`` on the ``insilico`` R function
        levels_prior (sequence): see ``levels.prior`` on the ``insilico`` R
            function
        levels_strength (float): see ``levels.strength`` on the ``insilico`` R
            function
        trunc_min (float): see ``trunc.min`` on the ``insilico`` R function
        trunc_max (float): see ``trunc.max`` on the ``insilico`` R function
        seed (int): see ``seed`` on the ``insilico`` R function
        exclude_impossible_cause (bool): ``exclude.impossible.cause`` on
            ``insilico`` R function
        missingness_threshold (float): see ``thre`` on the ``extract.prob`` R
            function
        learning_type (str): see ``type`` on the ``extract.prob`` R function
        n_level (int):  see ``nlevel.dev`` on the ``insilico.fit`` R function

    Attributes:
        R_PKG_NAME (str): name of the R package
        r_insilico (rpy2.InstalledSTPackage): python object for the converted
            R pacakge
        causes_ (list): sorted list of causes which appear in the training data
        symptoms_ (list): list of columns used to train the classifier
        symptoms_touse_ (list): list of columns which will used to predict.
            Columns in the training data with high proportions of missingness
            are dropped. See ``missingness_threshold`` to control this
        data_check_ (bool): Perform data checks in R. Some data checks do not
            work with non-InterVA-like inputs. The data are run if possible.
            This is calculated based on the values in the training data.
        data_check_missing_ (bool): Perform data checks for missingness in R.
            The caveat with ``data_check_`` applies.
        external_sep_ (bool): estimate external causes (injuries) separately.
            This feature is not supported for non-InterVa inputs and produces
            bugs if left as true with such input. If this flag is valid based
            on the values in the input data, this will take the value of
            ``external_sep``.
        exclude_impossible_cause_ (bool): This feature is not supported for
            non-InterVA inputs and produces bugs if left as true with such
            inputs. If this flag is valid based on the values in the input,
            data this will take the value of ``exclude_impossible_cause``.
        customized_ (bool): were non-InterVA inputs used
        prob_base_by_symp_dev_
        prob_base_
        gs_table_
        n_level_
        cond_prob_
        cond_prob_num_ (dataframe): result from ``extract_prob``
        cond_prob_alpha_ (dataframe): result from ``extract_prob``
        table_alpha_ (array): result from ``extract_prob``
        table_num_ (array): result from ``extract_prob``
        prob_base_dev_
    """
    R_PKG_NAME = 'InSilicoVA'

    def __init__(self,
                 update_cond_prob=None,
                 keep_prob_base_level=None,
                 external_sep=None,
                 n_sim=None,
                 thin=None,
                 burn_in=None,
                 auto_length=None,
                 conv_csmf=None,
                 jump_scale=None,
                 levels_prior=None,
                 levels_strength=None,
                 trunc_min=None,
                 trunc_max=None,
                 seed=None,
                 exclude_impossible_cause=None,
                 missingness_threshold=None,
                 learning_type=None,
                 n_level=None,
                 symptoms=None,
                 causes=None):
        self.update_cond_prob = update_cond_prob
        self.keep_prob_base_level = keep_prob_base_level
        self.external_sep = external_sep
        self.n_sim = n_sim
        self.thin = thin
        self.burn_in = burn_in
        self.auto_length = auto_length
        self.conv_csmf = conv_csmf
        self.jump_scale = jump_scale
        self.levels_prior = list(levels_prior) if levels_prior else None
        self.levels_strength = levels_strength
        self.trunc_min = trunc_min
        self.trunc_max = trunc_max
        self.seed = seed
        self.exclude_impossible_cause = exclude_impossible_cause
        self.missingness_threshold = missingness_threshold
        self.learning_type = learning_type
        self.n_level = n_level
        self.symptoms = symptoms
        self.causes = causes

        self.r_insilico = self.get_r_insilico_package()

    def fit(self, X, y=None):
        """Fit the estimator using training data.

        Train the classifier using symptom data and true
        causes. If ``None`` is passed to the classifier as the training data,
        it is fit with the default causes, symptoms and probbase provided by
        the Insilico software. For InSilicoVA, training involves calculating
        the probability of symptoms conditional on the true cause: P(S|C).
        This is performed in R using the method ``extract.prob``.

        Args:
            X (dataframe): training symptom data. Symptoms should be
                encoded as  0, 1, or -1 if using numeric encoding, or 'Y',
                '', '.' if using string encoding.
            y (series): true cause for each observation. Index must match the
                index of X.

        Returns:
            self

        See Also:
            extract_prob
        """
        # Remove previous predictions if refitting
        for attr in ['y_pred', 'csmf', 'converged']:
            setattr(self, attr, None)

        if X is None:
            warn('No training data provided. Using Insilico defaults.')
            self.causes_ = self.get_insilico_causes()
            self.symptoms_ = self.get_insilico_symptoms()
            self.symptoms_touse_ = self.symptoms_

            self.data_check_ = True
            self.data_check_missing_ = True
            self.exclude_impossible_cause_ = self.exclude_impossible_cause
            self.external_sep_ = self.external_sep

            trained_attrs = [
                'customized_',
                'prob_base_by_symp_dev_',
                'prob_base_',
                'cond_prob_num_',
                'gs_table_',
                'n_level_',
                'cond_prob_',
                'cond_prob_alpha_',
                'table_alpha_',
                'table_num_',
                'prob_base_dev_',
            ]
            for attr in trained_attrs:
                setattr(self, attr, None)
            return self

        if not (X.index == y.index).all():
            raise ValueError('X and y must have matching indicies.')

        if not (X.isin(['Y', '', '.']).all().all() or
                X.isin([1, 0, -1]).all().all()):
            raise ValueError('Symptoms are not properly encoded.')

        if self.symptoms:
            symptoms = X.columns.intersection(self.symptoms)
            if not symptoms.any():
                raise ValueError('None of the specified columns exist in the '
                                 'input dataframe.')
            else:
                X = X.loc[:, symptoms]
        else:
            X = X.copy()  # defensive copy, index will change in working copy

        self.symptoms_ = X.columns.tolist()
        self.causes_ = list(np.sort(y.unique()))

        # Always train on numerically encoded data. This seems to work better.
        try:
            X = X.replace({'Y': 1, '': 0, '.': -1})
        except TypeError:  # if all columns are already numeric
            pass
        X = X.astype(int)

        params = {}

        if self.learning_type in ['quantile', 'fixed', 'empirical']:
            params['learning_type'] = self.learning_type

        if self.missingness_threshold and 0 <= self.missingness_threshold <= 1:
            params['missingness_threshold'] = self.missingness_threshold

        probs = self.extract_prob(X, y, **params)

        self.cond_prob_ = probs.cond_prob
        self.cond_prob_alpha_ = probs.cond_prob_alpha
        self.table_alpha_ = probs.table_alpha
        self.table_num_ = probs.table_num
        self.symptoms_touse_ = probs.symps_train.columns.tolist()
        self.gs_table_ = probs.cond_prob.columns.tolist()

        insilico_causes = self.get_insilico_causes()
        insilico_symptoms = self.get_insilico_symptoms()

        # Add training parameters which will be used by ``insilico.fit``
        if (X.columns.isin(insilico_symptoms).all() and
                y.isin(insilico_causes).all()):
            warn('InterVA format detected')
            # The probbase file must be in the correct order with no
            # missingness
            prob_base = probs.cond_prob.loc[insilico_symptoms, insilico_causes]
            prob_base = prob_base.fillna(0)

            # Insilico tests for impossible causes by looking at the
            # conditional probabilities of all the causes paired with the
            # first 9 symptoms (7 age groups and both sexes). If any of these
            # demographic indicators have a probability of zero they are
            # labeled as impossible. If none of these are zero, R fails with a
            # cryptic message about data should be vector and recieved NULL.
            # Gaurd against this corner case by testing in python and passing
            # exclude_impossible_cause=True if necessary
            demog_symps = ['elder', 'midage', 'adult', 'child', 'under5',
                           'infant', 'neonate', 'male', 'female']
            if not (prob_base.loc[demog_symps] == 0).any().any():
                self.exclude_impossible_cause_ = False
            else:
                self.exclude_impossible_cause_ = self.exclude_impossible_cause

            # If Insilico format is detect this must be reset to the complete
            # symptom list or it will not pass the Insilico data cleaning
            # process.
            self.symptoms_touse_ = self.symptoms_

            self.customized_ = None
            self.data_check_ = True
            self.data_check_missing_ = True
            self.external_sep_ = self.external_sep
            self.prob_base_by_symp_dev_ = None
            self.n_level_ = None
            self.prob_base_ = prob_base.values
            self.prob_base_dev_ = None
            self.table_alpha_ = None
            self.table_num_ = None
            self.gs_table_ = None
        else:
            warn('Custom format detected')
            self.customized_ = True
            self.data_check_ = False
            self.data_check_missing_ = False
            self.external_sep_ = False   # no way to list them
            self.exclude_impossible_cause_ = False   # no way to list them
            self.prob_base_by_symp_dev_ = False
            self.n_level_ = self.n_level
            self.prob_base_ = probs.cond_prob.values
            self.prob_base_dev_ = probs.cond_prob_alpha

            # See `https://github.com/richardli/InSilicoVA/blob/master/
            # InSilicoVA/R/insilico_train.r` lines 105-111
            if self.update_cond_prob and self.learning_type != 'empirical':
                self.prob_base_ = probs.cond_prob_alpha
                self.cond_prob_num_ = None
            else:
                self.prob_base_ = probs.cond_prob
                self.cond_prob_num_ = probs.cond_prob

        return self

    def predict(self, X):
        """Predict using the InsilicoVA algorithm.


        Warning:
            When using the default causes and symptoms, the prediction will
            exclude observations with valid age and sex data. This is because
            the R methods silently drop these rows.

        Args:
            X (dataframe): training symptom data. Symptoms should be
                encoded as  0, 1, or -1 if using numeric encoding, or 'Y',
                '', '.' if using string encoding.

        Returns:
            predictions:

                * indiviual (series)
                * csmf (series)

        See Also:
            insilico_fit
        """
        if not (X.isin(['Y', '', '.']).all().all() or
                X.isin([1, 0, -1]).all().all()):
            raise ValueError('Symptoms are not properly encoded')

        df = X.loc[:, X.columns.intersection(self.symptoms_touse_)]
        if not df.columns.any():
            raise ValueError('None of the columns from the training data '
                             'appear in the input data.')

        # The R code does not adequately handle the numeric encoding for all
        # steps of the data cleaning for all combinations of input parameters,
        # especially customized non-InterVA formats. Ensure that the data
        # passed to R always uses the string encoding
        df = df.replace({1: 'Y', 0: '', -1: '.'})

        # The R code does not adequately handle cases where there are no
        # injury symptoms endorsed and the default value `external.sep=TRUE`
        # is passed. In these cases, when the code goes to separate rows with
        # external causes, it will fail trying to assign to an empty matrix.
        # This can be avoided by passing `external_sep=FALSE` if no
        # observations have injuries. This occurs for neonates who were not
        # asked questions about injuries. It fails for the same reason at a
        # different place if passed a dataset with all injuries.
        if not self.customized_:
            inj = ['injury', 'traffic', 'o_trans', 'fall', 'drown', 'fire',
                   'assault', 'venom', 'force', 'poison', 'inflict', 'suicide']
            if not df.columns.intersection(inj).any():
                self.external_sep_ = False
            elif not (df[df.columns.intersection(inj)] == 'Y').any().any():
                self.external_sep_ = False
            elif (df[df.columns.intersection(inj)] == 'Y').any(1).all():
                raise ValueError('Insilico cannot handle datasets where all '
                                 'observations report injuries.')

        # As part of the data cleaning, Insilico removes data with no age data
        # or with no sex data or with no symptom data. This occurs within the
        # `removeBad` method and does not issue any warnings. If all the rows
        # have errors an empty dataframe is passed returned. This then fails
        # with a cryptic indexing-reassigning error shortly after.
        if not self.customized_:
            age_cols = ['elder', 'midage', 'adult', 'child', 'under5',
                        'infant', 'neonate']
            has_age = (df[df.columns.intersection(age_cols)] == 'Y').any(1)
            has_sex = (df[['male', 'female']] == 'Y').any(1)
            # Line 254 of insilico_core.r checks columns 23 to 223 for at
            # least one endorsement
            has_symps = (df.iloc[:, 22:222] == 'Y').any(1)
            valid = df.loc[has_age & has_sex & has_symps]
            if not len(valid):
                raise ValueError('No observations have a complete set of '
                                 'age and sex data.')
            dropped = len(df) - len(valid)
            if dropped:
                warn('{} observations do not have valid age and sex data '
                     'and will be dropped before predicting'.format(dropped))

        # The original index of X may not be unique. For the validation study
        # the rows are resampled with replacement, which create duplicates.
        # R expects a unique rowname. Setting the index to a dummy stringified
        # range index ensures the corresponding output data can be matched to
        # input data and sorted appropriately
        new_indicies = ['I{}'.format(i) for i in range(len(df))]
        index_map = dict(zip(new_indicies, df.index))
        df.index = new_indicies

        # Values with trailing underscores are calculated in the fit
        # other values are passed through (possibly renamed)
        params = {
            # Data processing parameters
            'isNumeric': False,
            # 'updateCondProb': self.update_cond_prob_,
            'keepProbbase_level': self.keep_prob_base_level,
            # 'CondProb': self.cond_prob_alpha_,
            'CondProbNum': self.prob_base_,
            'datacheck': self.data_check_,
            'datacheck_missing': self.data_check_missing_,
            'warning_write': False,
            'external_sep': self.external_sep_,

            # Actual fit parameters (things to grid-search over)
            'Nsim': self.n_sim,
            'thin': self.thin,
            'burnin': self.burn_in,
            'auto_length': self.auto_length,
            'conv_csmf': self.conv_csmf,
            'jump_scale': self.jump_scale,
            'levels_prior': self.levels_prior,
            # 'levels_strength': self.levels_strength_,
            'trunc_min': self.trunc_min,
            'trunc_max': self.trunc_max,
            'seed': self.seed,
            'exclude_impossible_cause': self.exclude_impossible_cause_,

            # Customizations to fit data
            'customization_dev': self.customized_,
            'Probbase_by_symp_dev': self.prob_base_by_symp_dev_,
            'probbase_dev': self.prob_base_dev_,
            'table_dev': self.table_alpha_,
            'table_num_dev': self.table_num_,
            'gstable_dev': self.gs_table_,
            'nlevel_dev': self.n_level_,
        }

        # R is not liking kwargs with values set the rpy2 NULL
        # Removing these kwargs from params seems to work the same. There
        # shouldn't be a param which accepts NULL where NULL is not the
        # default (NULL should never override a default)
        params = {k: v for k, v in params.items() if v is not None}

        fitted = self.insilico_fit(df, **params)

        # Reorder to rows to match the original order
        if fitted.indiv_prob.index.symmetric_difference(df.index).any():
            if fitted.indiv_prob.index.difference(df.index).any():
                raise BaseException('Unknown indicies returned by Insilico.')
            missing = set(df.index).difference(fitted.indiv_prob.index)
            if missing:
                warn('{} observations with no predictions. These will be '
                     'set to undetermined.'.format(len(missing)))
        indiv = fitted.indiv_prob.loc[df.index]
        csmf = fitted.csmf

        # Map the dummy indices back to the original input indicies
        indiv.index = indiv.index.to_series().map(index_map)

        cause_renames = self.get_labels_map(self.causes_)
        indiv.columns = indiv.columns.to_series().map(cause_renames)
        csmf.columns = csmf.columns.to_series().map(cause_renames)

        # Take the most probable prediction as the individual level prediction
        y_pred = indiv.apply(self.indiv_most_probable, axis=1)

        # Insilico might say there is a small probably of a cause occuring
        # even if the conditional probability for all symptoms is zero. This
        # leads to a very small amount in lots of causes. If the default
        # cause list is used all sixty causes have a mean CSMF above zero.
        # This should be removed and scaled to on to provide more comparable
        # CSMF for accuracy measures
        csmf = csmf.mean().loc[self.causes_]
        csmf = csmf / csmf.sum()

        self.converged_ = fitted.converged
        return y_pred, csmf

    @classmethod
    def get_r_insilico_package(cls):
        """Return the ``rpy2`` object for the Insilico package."""
        return importr(cls.R_PKG_NAME)

    def get_sample_data(self):
        """Return the RandomVA1 sample data from the Insilico pacakge as a
           pandas dataframe."""
        # In R, bring the example dataframe into memory
        robjects.r('library("{}")'.format(self.R_PKG_NAME))
        robjects.r('data(RandomVA1)')

        # Return as a pandas dataframe
        df = ri2py(robjects.r['RandomVA1'])
        df = df.set_index('ID')
        return df

    def get_cond_prob_num(self):
        """Return the condprobnum file from the Insilico package as a pandas
           dataframe."""
        rbase = importr('base')
        robjects.r('library("{}")'.format(self.R_PKG_NAME))
        robjects.r('data(condprobnum)')
        # robjects.r('df <- data.frame(condprobnum)')
        df = ri2py(rbase.data_frame(robjects.r['condprobnum']))
        df = df.T
        df.index = list(robjects.r('colnames(condprobnum)'))
        return df

    def get_insilico_causes(self):
        """Returns a list of the causes used in the Insilico package."""
        # Add the condprob file to the R global environment.
        # This is a data.matrix which ships with the package
        # The rows are symptoms and the columns are causes
        robjects.r('library("{}")'.format(self.R_PKG_NAME))
        robjects.r('data(condprobnum)')
        return list(robjects.r('colnames(condprobnum)'))

    def get_insilico_symptoms(self):
        """Return a list of symptom predictors used in the Insilico package."""
        # Add the condprob file to the R global environment.
        # This is a data.matrix which ships with the package
        # The rows are symptoms and the columns are causes
        robjects.r('library("{}")'.format(self.R_PKG_NAME))
        robjects.r('data(condprobnum)')
        return list(robjects.r('rownames(condprobnum)'))

    def get_insilico_short_causes(self):
        """Return a dict to map from short to long cause names derived from
           the InsilicoVA caustext file."""
        rbase = importr('base')

        # Add the causetext file to the R global environment.
        # This is a data.matrix which ships with the package.
        # Casting to a data.frame adds the dimnames to the object
        # extracted by rpy2
        robjects.r('data(causetext)')
        robjects.r('cause_df <- data.frame(causetext)')
        causetext = ri2py(rbase.data_frame(robjects.r['cause_df']))

        causetext.columns = ['short', 'long', 'v3']
        causetext = causetext.loc[causetext.short.str.startswith('B_')]
        return dict(zip(causetext.short, causetext.long))

    def extract_prob(self, X, y, learning_type=None,
                     missingness_threshold=None):
        """Extract conditional probabilities from training data

        Use the Insilico R package to extract condtional probabilities from
        training data. The ouput is used as inputs into the prediction. This
        essentially just wraps the call to R which in turn wraps a call to
        java. The positional arguments are slightly different than the R method
        and the keyword arguments have been slightly renamed.

        The R method expects a dataframe, a str of a column name in that
        dataframe, and a list of values in that column. Instead, this method
        takes dataframe without the attached column and a series of the
        predicted classes (sklearn-style: X, y). The values of the series are
        calculated for you. (You're welcome.)

        Documentation for the R method can be found at
        `<https://cran.r-project.org/web/packages/InSilicoVA/InSilicoVA.pdf>`_


        Args:
            X (dataframe): training data with all columns codes as predictors.
                The index should be set to the row identifier and all columns
                should be symptoms encoded as either 1 for yes, 0 for no, and
                -1 for missing or 'Y' for yes, '' for no, and '.' for missing
            y (series): sequence of true prediction class for observations
            learning_type (str): value should be 'quantile', 'fixed' or
                'empirical'. See the R package documentation for descriptions
            missingness_threshold (float): value between 0 and 1. If the
                proportion of missingness for a predictor is above this
                threshold it is dropped from the analysis.

        Returns:
            (namedTuple): InsilicoTrained:

                * cond_prob (dataframe): matrix of numbers
                * cond_prob_alpha (dataframe): matrix of letters
                * table_num (np.array): list of numbers
                * table_alpha (np.array): list of letters
                * symps_train (dataframe): with only values used

        See Also:
            fit
        """
        if not (X.index == y.index).all():
            raise ValueError('X and y must have matching indicies')

        if X.isin([1, 0, -1]).all().all():
            is_numeric = True
        elif X.isin(['Y', '', '.']).all().all():
            is_numeric = False
        else:
            raise ValueError('Symptoms are not properly encoded')
        X = X.copy()

        rbase = importr('base')
        robjects.r('library("{}")'.format(self.R_PKG_NAME))
        pandas2ri.activate()

        # Dataframes in R cannot have numeric dimnames labels. rpy2 is
        # converting some special characters into periods. The predictors
        # (symptoms) and true classes (causes) both become labels for
        # different output matrices. To avoid cross language data conversion
        # issue, all labels will be encoded into safe simple strings and
        # decoded after data is returned to python
        new_symptoms = ['S{}'.format(i) for i, s in enumerate(X.columns)]
        symptoms_map = dict(zip(new_symptoms, X.columns))

        def symptoms_map_(x):
            return symptoms_map[x]

        encode_causes = {c: 'GS{}'.format(i) for i, c in enumerate(set(y))}
        decode_causes = {v: k for k, v in encode_causes.items()}

        def decode_causes_(x):
            return decode_causes[x]

        # Insilico is assuming the y_actual values are attatched to the
        # dataframe. Ensure the names of the added column does not conflict
        # with an existing column. Do this before changing the index.
        gs = 'xxGS'
        while gs in X.columns:
            gs = 'x{}'.format(gs)
        X[gs] = y.map(encode_causes)

        # The original index of X may not be unique. For the validation study
        # the rows are resampled with replacement, which create duplicates. R
        # expects a unique rowname. Setting the index to a dummy stringified
        # range index ensures the corresponding output data can be matched to
        # input data and sorted into the original order
        new_index = ['I{}'.format(i) for i, x in enumerate(X.index)]
        index_map = dict(zip(new_index, X.index))

        def index_map_(x):
            return index_map[x]

        # Insilico is expecting that the first column in the dataframe is a
        # string containing the ID. However, this is dropped, and the dimnames
        # attribute of the matrix is set to the index of the passed pandas
        # dataframe. Both the index and first column should be set to the new
        # encoded index value. Ensure the names of the added columns do not
        # conflict with an existing column
        X.index = new_index
        X = X.reset_index()
        X = X.set_index(X.columns[0], drop=False)

        id_col = 'xxID'
        while id_col in X.columns:
            id_col = 'x{}'.format(id_col)
        X.columns = [id_col] + new_symptoms + [gs]

        # Grab a list of the encoded causes to pass to insilico.
        gs_list = X[gs].sort_values().unique()

        # Only pass parameters which are explictly set
        params = {
            'isNumeric': is_numeric,
            'type': learning_type,
            'thre': missingness_threshold
        }
        params = {k: v for k, v in params.items() if v is not None}
        fit = self.r_insilico.extract_prob(X, gs, gs_list, **params)

        rows, cols = tuple(rbase.dimnames(fit.rx2('cond.prob')))
        cond_prob = ri2py(rbase.data_frame(fit.rx2('cond.prob')))
        cond_prob.index = map(symptoms_map_, rows)
        cond_prob.columns = map(decode_causes_, cols)

        if learning_type == 'empirical':
            # These are not calculated when empirical learning is used
            probs_alpha = None
            table_alpha = None
            table_num = None
        else:
            rows, cols = tuple(rbase.dimnames(fit.rx2('cond.prob.alpha')))
            probs_alpha = ri2py(rbase.data_frame(fit.rx2('cond.prob.alpha')))
            probs_alpha.index = map(symptoms_map_, rows)
            probs_alpha.columns = map(decode_causes_, cols)
            table_alpha = ri2py(fit.rx2('table.alpha'))
            table_num = ri2py(fit.rx2('table.num'))

        rows, cols = tuple(rbase.dimnames(fit.rx2('symps.train')))
        symps_train = ri2py(fit.rx2('symps.train'))
        try:
            symps_train.index = map(index_map_, rows)
        except KeyError:
            symps_train.index = map(index_map_, new_index)
        symps_train.columns = map(symptoms_map_, cols)

        attrs = [
            'cond_prob',
            'cond_prob_alpha',
            'table_alpha',
            'table_num',
            'symps_train'
        ]
        InsilicoTrained = namedtuple('InsilicoTrained', attrs)
        pandas2ri.deactivate()
        return InsilicoTrained(
            cond_prob,
            probs_alpha,
            table_alpha,
            table_num,
            symps_train
        )

    def insilico_fit(self, df, **kwargs):
        """Predict cause of death using the Insilcio R package

        This is a wrapper around the ``insilico.fit`` method from the R
        packages. All key word arguments are passed directly to the method as
        is. Periods (".") in kwargs should be replaced with underscores ("_")
        to match rpy2 conversion conventions.

        Args:
            df (dataframe): test data. All columns should be symptoms the index
                should be set to a non-numeric string. Index values should be
                unique. Symptoms should be coded appropriately according to
                the ``isNumeric`` keyword (which defaults to False in R).

        Returns:
            InsilicoFit (namedTuple): attributes extracted from the object
                return by ``insilico.fit``

        See Also:
            predict
        """
        # R dataframes cannot have duplicate indicies
        if not df.index.is_unique:
            raise ValueError('Dataframes in R must have unique indicies.')

        is_numeric = kwargs.get('isNumeric', False)
        encoding = [1, 0, -1] if is_numeric else ['Y', 'y', '', '.']
        if not df.isin(encoding).all().all():
            raise ValueError('Values are not properly encoded for isNumeric={}'
                             .format(is_numeric))

        # The dataframe must have the index as both the index and as the first
        # column of the dataframe. The first column will be dropped in the R
        # methods and the index will be returned as by rpy2.
        df = df.reset_index().set_index(df.columns[0], drop=False)

        rbase = importr('base')

        # Automatically convert Pandas and R dataframes for just the fit.
        # Leaving pandas2ri activated changes global settings and results in
        # type errors in other functions using dataframes and rpy2 when called
        # in the same session (including pytests).
        pandas2ri.activate()

        # rpy2 isn't converting `None` to `NULL` for kwargs. Passing `False`
        # instead of `None` leads to R Runtime errors.
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        fit = self.r_insilico.insilico_fit(df, **kwargs)

        # Determine if all the causes above the threshold converged
        # The convergence test is unstable for small proportions so only
        # causes with a CSMF above the threshold pass to fit are examined
        # We only care about the summary result and not the details so pass
        # verbose=False to avoid mucking around with a returned heidel.diag
        # object
        conv_csmf = kwargs.get('conv_csmf', 0.02)
        test_conv = self.r_insilico.csmf_diag(fit, conv_csmf=conv_csmf,
                                              test='heidel', verbose=False)
        converged = np.all(ri2py(test_conv))

        # Extract all attributes from Insilico fit
        # Casting matrices to dataframes in R adds the dimnames to the object
        # converted by rp2 which eliminates the need to extract them separately
        sid = ri2py(fit.rx2('id'))  # avoid python reserved word
        data = ri2py(rbase.data_frame(fit.rx2('data')))
        indiv_prob = ri2py(rbase.data_frame(fit.rx2('indiv.prob')))
        csmf = ri2py(rbase.data_frame(fit.rx2('csmf')))
        if isinstance(fit.rx2('conditional.probs'), RNULLType):
            cond_probs = None
        else:
            cond_probs = ri2py(rbase.data_frame(fit.rx2('conditional.probs')))
        if isinstance(fit.rx2('conditional.probs'), RNULLType):
            prob_base = None
        else:
            prob_base = ri2py(rbase.data_frame(fit.rx2('probbase')))
        if isinstance(fit.rx2('missing.symptoms'), RNULLType):
            missing_symptoms = None
        else:
            missing_symptoms = ri2py(fit.rx2('missing.symptoms'))
        external = bool(list(fit.rx2('external'))[0])
        if isinstance(fit.rx2('external.causes'), RNULLType):
            external_causes = None
        else:
            external_causes = ri2py(fit.rx2('external.causes'))
        if isinstance(fit.rx2('impossible.causes'), RNULLType):
            impossible_causes = None
        else:
            impossible_causes = ri2py(fit.rx2('impossible.causes'))
        update_cond_prob = bool(list(fit.rx2('updateCondProb'))[0])
        keep_prob_base_level = bool(list(fit.rx2('keepProbbase.level'))[0])
        data_check = bool(list(fit.rx2('datacheck'))[0])
        n_sim = int(list(fit.rx2('Nsim'))[0])
        thin = int(list(fit.rx2('thin'))[0])
        burn_in = int(list(fit.rx2('burnin'))[0])
        jump_scale = float(list(fit.rx2('jump.scale'))[0])
        levels_prior = ri2py(fit.rx2('levels.prior'))
        levels_strength = float(list(fit.rx2('levels.strength'))[0])
        trunc_min = float(list(fit.rx2('trunc.min'))[0])
        trunc_max = float(list(fit.rx2('trunc.max'))[0])
        if isinstance(fit.rx2('subpop'), RNULLType):
            subpop = None
        else:
            subpop = ri2py(fit.rx2('subpop'))
        if isinstance(fit.rx2('indiv.CI'), RNULLType):
            indiv_ci = None
        else:
            indiv_ci = float(list(fit.rx2('indiv.CI'))[0])
        is_customized = bool(list(fit.rx2('is.customized'))[0])

        attrs = [
            'sid',
            'data',
            'indiv_prob',
            'csmf',
            'conditional_probs',
            'prob_base',
            'missing_symptoms',
            'external',
            'external_causes',
            'impossible_causes',
            'update_cond_prob',
            'keep_prob_base_level',
            'data_check',
            'n_sim',
            'thin',
            'burn_in',
            'jump_scale',
            'levels_prior',
            'levels_strength',
            'trunc_min',
            'trunc_max',
            'subpop',
            'indiv_ci',
            'is_customized',
            'converged',
        ]
        InsilicoFit = namedtuple('InsilicoFit', attrs)
        pandas2ri.deactivate()
        return InsilicoFit(
            sid,
            data,
            indiv_prob,
            csmf,
            cond_probs,
            prob_base,
            missing_symptoms,
            external,
            external_causes,
            impossible_causes,
            update_cond_prob,
            keep_prob_base_level,
            data_check,
            n_sim,
            thin,
            burn_in,
            jump_scale,
            levels_prior,
            levels_strength,
            trunc_min,
            trunc_max,
            subpop,
            indiv_ci,
            is_customized,
            converged,
        )

    @staticmethod
    def get_labels_map(labels):
        """Returns a mapping dictionary to convert modified strings back

        ``insilico.fit`` modifies column headers by removing all non-alphabetic
        characters, including spaces. All special characters are replaces with
        periods ('.') so back translation is impossible without knowing the
        original. When the original are known the modified version can be
        calculated.

        Args:
            labels (list of strings)

        Returns:
            mapping (dict): keys are modified strings, values are originals
        """
        re_not_letter = re.compile('[^A-Za-z]')
        return {re_not_letter.sub('.', str(label)): label for label in labels}

    @staticmethod
    def indiv_most_probable(series):
        """Return the index of the largest value in a series"""
        if len(series.unique()) == 1:
            return 'Undetermined'
        else:
            return series.sort_values(ascending=False).first_valid_index()
