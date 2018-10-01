import functools
import math
import os
import sys

import pandas as pd

from prep import REPO_DIR, load_cleaned_file


MAPPED_DIR = os.path.join(REPO_DIR, 'data', 'mapped')


def mapped_filepath(symptoms, module, hce=True):
    """Load the mapped symptom files.

    Args:
        symptoms (str): 'insilico', 'tariff'
        module (str): 'adult', 'child', 'neonate' or 'codebook'
        hce (bool): should health care experience columns be included. If
            False they will be present and set to missing.

    Returns:
        (str)
    """
    hce = 'hce' if hce else 'no_hce'
    filename = 'mapped_{}_{}_{}.csv'.format(symptoms, module, hce)
    return os.path.join(MAPPED_DIR, filename)


def has_any(row, mapping=None):
    """Determine if a row of data has any column matching the given value

    Args:
        row (series): single row of cleaned data
        mapping (dict): column -> value required for endorsement

    Returns:
        endorsement (int): 0 or 1
    """
    for col, val in mapping:
        if row[col] == val:
            return 1
    return 0


def has_all(row, mapping=None):
    """Deterime if a row of data matches multiple critieria.

    Args:
        row (series): single row of cleaned data
        mapping (dict): column -> value required for endorsement

    Returns:
        endorsement (int): 0 or 1
    """
    has = True
    for col, val in mapping:
        has = has and row[col] == val
    return int(has)


def value(x, val=None):
    return int(x == val)


def less_than(x, val=0):
    return int(x < val)


def at_least(x, val=0):
    return int(x >= val)

def no_more_than(x, val=0):
    return int(x <= val or pd.isnull(x))


def between(x, lower=0, upper=1):
    return int(lower <= x <= upper)


def no_data():
    return float('nan')


def definitely_not(x):
    return 0


# Mapping functions
# Each must take only one parameter, either a cell or row
zero = functools.partial(value, val=0)
one = functools.partial(value, val=1)
two = functools.partial(value, val=2)
three = functools.partial(value, val=3)
four = functools.partial(value, val=4)


def map_symptoms(data, mapping):
    """Map cleaned PHMRC data to binary symptoms indicators.

    The map consists of a list of tuples with one entry for each target column
    in the fully mapped data. The first value is the target column name. The
    second value describes the column and possibly values in the original data
    which are used. The third value is a function used in the input data to
    convert it to the value for the target column.

    Args:
        data (dataframe): cleaned GHDx data
        mapping (list of tuples)

    Returns:
        (dataframe)
    """
    # Setup the output dataframe with the same index as the input
    df = pd.DataFrame(index=data.index)
    df.index.name = 'ID'

    print('{} features detected:'.format(len(mapping)), end='')
    digits = math.ceil(math.log10(len(mapping)))

    for i, (target, source, fn) in enumerate(mapping):

        if not i % 50:
            print('\n {:0{}d} '.format(i, digits), end='')
        sys.stdout.flush()
        print('.', end='')
        sys.stdout.flush()

        # Column has no mapping but should be in the output dataframe
        if source is None:
            df[target] = float('nan')

        # Column maps from one PHMRC column
        try:
            str_type = basestring
        except NameError:
            str_type = str

        if isinstance(source, str_type):
            df[target] = data[source].map(fn)

        # Insilico column maps from multiple PHMRC columns
        if isinstance(source, list):
            df[target] = data.apply(fn, axis=1, args=(source,))

    print('')
    return df


def map_all_modules(dataset, mapping, hce_columns):
    """Map and save data for all modules to binary symptom files.

    Two files are saved for each module. The first contains the fully mapped
    data. The second includes the same columns, but all ``hce_columns`` have
    been set to missing. The value for missing depends on the set of symptoms.
    For InSilicoVA symptoms ``-1`` is used for missing. For Tariff 2.0 symptoms
    ``0`` is used for missing.

    Args:
        dataset (str): 'tariff' or 'insilico'
        mapping (dict of list of tuples)
        hce_columns (dict of list of str): health care experience column
            labels by module
    """
    try:
        os.mkdir(MAPPED_DIR)
    except OSError:
        pass   # folder already exists

    missing = -1 if dataset == 'insilico' else 0
    for module in ['adult', 'child', 'neonate']:
        print('Mapping {} data to the {} feature set'.format(module, dataset))
        df = map_symptoms(load_cleaned_file(module), mapping[module])
        df = df.fillna(missing)
        df.to_csv(mapped_filepath(dataset, module, hce=True))

        df.loc[:, hce_columns[module]] = missing
        df.to_csv(mapped_filepath(dataset, module, hce=False))

    print('Files are saved in {}'.format(MAPPED_DIR))
