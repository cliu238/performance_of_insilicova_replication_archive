from __future__ import print_function
import argparse
import os

import pandas as pd

from insilico import InsilicoClassifier
from map_insilico import INSILICO_CAUSE_MAP
from validation import (
    RandomClassifier,
    validate,
    out_of_sample_splits,
    in_sample_splits,
    no_training_splits,
)
from prep import REPO_DIR, SITES, load_cleaned_file
from mapping import mapped_filepath


def get_sites_and_causes(module, cause_list):
    """Returns the sites and causes for a given module

    Args:
        module (str): 'adult', 'child', or 'neonate'
        cause_list (str): 'insilico', or 'phmrc'

    Returns:
        sites (series): encoded sites for each observation
        causes (series): gold standard cause for each observation
    """
    df = load_cleaned_file(module)

    # Sklearn model selectors expect numerically encoded group sequences
    # Sites are uses as the groups for the holdout model selector
    sites = df.site.map(dict([(s, i) for i, s in enumerate(SITES)]))

    if cause_list == 'insilico':
        causes = df.gs_text46.map(INSILICO_CAUSE_MAP[module])
    elif cause_list == 'phmrc':
        causes = df.gs_text34
    else:
        raise ValueError('Unknown cause_list: "{}"'.format(cause_list))
    return sites, causes


def main(**kwargs):
    """Run analysis

    Args:
        Anything you want...Maybe I'll use it. May I won't.

    Returns:
        (tuple of dataframes): sames as ``prediction_accuracy``
    """
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    clf = config_classifier(kwargs['clf'], dict(kwargs.get('params', [])))

    filename = mapped_filepath(kwargs['symptoms'], kwargs['module'],
                               hce=kwargs.get('hce', True))
    symptoms = pd.read_csv(filename, index_col=0)

    sites, gs = get_sites_and_causes(kwargs['module'], kwargs['cause_list'])

    spliter_params, validate_params, name_tags = get_params(**kwargs)

    outdir = kwargs.get('outdir')

    analysis = kwargs.get('analysis')
    if analysis == 'no-train':
        if not outdir:
            outdir = os.path.join(REPO_DIR, 'data', 'default')
        spliter = no_training_splits(symptoms, gs, **spliter_params)
    elif analysis == 'in-sample':
        if not outdir:
            outdir = os.path.join(REPO_DIR, 'data', 'in_sample')
        spliter = in_sample_splits(symptoms, gs, **spliter_params)
    elif analysis == 'validate':
        if not outdir:
            outdir = os.path.join(REPO_DIR, 'data', 'validate')
        spliter = out_of_sample_splits(symptoms, gs, **spliter_params)
    else:
        raise ValueError('Unknown analysis: "{}"'.format(analysis))

    try:
        os.makedirs(outdir, exist_ok=True)
    except OSError:
        pass

    output = validate(symptoms, gs, clf, spliter, **validate_params)

    filenames = ['predictions', 'csmf', 'ccc', 'accuracy']
    for i, f in enumerate(filenames):
        filename = '{}_{}.csv'.format('_'.join(name_tags), f)
        output[i].to_csv(os.path.join(outdir, filename), index=False)

    return output


def get_params(**kwargs):
    """Process the args into parameters for the validation analyses

    Args:
        Anything you want...Maybe I'll use it. May I won't.

    Returns:
        params (dict): kwargs for out-of-sample accuracy
        name_tags (list): strings to concatenate at the end of filenames
            to ensure parameters sets save to unique files
    """
    analysis = kwargs['analysis']
    module = kwargs['module']

    clf = kwargs.get('clf')
    symptoms = kwargs.get('symptoms')
    cause_list = kwargs.get('cause_list')
    hce = kwargs.get('hce', True)
    subset = kwargs.get('subset')
    if subset:
        subset_tag = '-'.join(map(str, subset))
    else:
        subset_tag = '0-{}'.format(kwargs['n_splits'])

    hce_tag = 'w_hce' if hce else 'no_hce'

    validate_params = {
        'resample_test': kwargs.get('resample_test', True),
        'resample_size': kwargs.get('resample_size'),
        'subset': subset,
    }
    spliter_params = {
        'n_splits': kwargs.get('n_splits'),
    }

    if analysis == 'no-train':
        filename_tags = ['default', clf, module, hce_tag, subset_tag]

    elif analysis == 'in-sample':
        filename_tags = ['in_sample', clf, module, hce_tag, cause_list,
                         symptoms, subset_tag]

    elif analysis == 'validate':
        filename_tags = ['validate', clf, module, hce_tag, cause_list,
                         symptoms, subset_tag]
        spliter_params['random_state'] = kwargs.get('split_seed')

    else:
        raise ValueError('Unknown analysis: "{}"'.format(analysis))

    return spliter_params, validate_params, filename_tags


def config_classifier(clf, params=None):
    """Process the args for the classifier

    Args:
        clf (str): name of sklearn-like classifier object. Currently only
            'insilico' and 'random' are supported
        params (dict): params initialize the classifier object

    Returns:
        classifier: Sklearn-like classifer with fit and predict methods
    """
    if params:
        for k, v in params.items():
            try:
                try:
                    params[k] = int(v)
                except ValueError:
                    params[k] = float(v)
            except ValueError:
                params[k] = v
    else:
        params = dict()

    if clf == 'insilico':
        clf = InsilicoClassifier(**params)
    elif clf == 'random':
        clf = RandomClassifier(**params)
    else:
        raise ValueError('Unknown classifier: "{}"'.format(clf))
    return clf


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Analyze a classifer using the validation framework.'
    )

    # Data parameters
    parser.add_argument(
        '-m', '--module', required=True, choices=['adult', 'child', 'neonate'],
        help='Which age-specific module should be analyzed')
    parser.add_argument(
        '-s', '--symptoms', required=True, choices=['tariff', 'insilico'],
        help='Which set of symptoms predictors should be used')
    parser.add_argument('--no-hce', action='store_false', dest='hce',
                        help='Drop Health Care Experience symptoms')
    parser.add_argument(
        '-c', '--cause-list', required=True, choices=['insilico', 'phmrc'],
        help='Which set of causes should the classifier predict')
    parser.add_argument('-o', '--outdir', default=None,
                        help='Output directory for saved files')

    # Classifier parameters
    parser.add_argument(
        '--clf', default='insilico', choices=['insilico', 'random'],
        help='Classifer used to make predictions')
    parser.add_argument(
        '-p', '--params', action='append', nargs=2,
        help=('Enter space separated key-value pairs which will be passed to '
              'the classifier when initialized'))

    # Validation Parameters
    parser.add_argument(
        '-a', '--analysis', default='validate',
        choices=['validate', 'in-sample', 'no-train'],
        help='Which analysis should be run')
    parser.add_argument(
        '--no-test-resamp', action='store_false', dest='resample_test',
        help='Skip resampling the test data before predicitng')
    parser.add_argument(
        '--resample-size', type=float, default=1,
        help=('Factor to multiply the number of observations in the test '
              'split by when resampling the data'))
    parser.add_argument(
        '--subset', default=None, type=int, nargs=2,
        help=('Define the range of splits implemented in this run. Pass two '
              'ints separated by a spaces. Numbers should range between 0 and '
              'splits minus 1'))
    parser.add_argument(
        '--n-splits', type=int, default=2,
        help='Number of splits for split model selector')
    parser.add_argument(
        '--test-size', type=float, default=0.25,
        help='Proportion of the data used in the test split')
    parser.add_argument(
        '--split-seed', type=int, default=None,
        help='Seed used for split model selector')
    parser.add_argument(
        '--holdout-n', type=int, default=1,
        help='Number of sites tp hold from the training split and use in test '
             'split. Max=5 (There are only six sites in the data.)')
    args = parser.parse_args()
    print(args)
    main(**vars(args))
