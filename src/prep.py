from __future__ import print_function
import os
import re
import sys

import pandas as pd

from download import REPO_DIR, load_ghdx_data, filter_DtypeWarnnings


SITES = ['AP', 'Bohol', 'Dar', 'Mexico', 'Pemba', 'UP']
CLEANED_DATA_DIR = os.path.join(REPO_DIR, 'data', 'cleaned')


def clean_codebook(codebook):
    """Clean the codebock and add information about column type.

    This function:
        * indexes the dataframe on the ``variable`` column
        * adds a data type column which is used for cleaning
        * drops one column which does not appear in the data
        * adds a missing space in a value in the coding column to aid in
          parsing coding strings when recoding values
        * adds a missing sentinel value for child weight variables
        * renames the ``health_care_experience`` column to ``hce``

    Args:
        codebook (dataframe): original GHDx codebook

    Returns:
        (dataframe)
    """
    df = codebook.set_index('variable')

    df.loc[df.coding.notnull(), 'type'] = 'categorical'
    df.loc[df.coding.isnull(), 'type'] = 'numeric'
    df.loc[df.index.str.startswith('word_'), 'type'] = 'word'
    df.loc[['site', 'g2_01', 'g2_02'], 'type'] = 'info'

    # Some numeric variables have a sentinel value for missing which appears
    # in the coding coding. This value is always a set of 9s as "Don't Know"
    # Since this is the only coding it appears at the begining of the string
    num_with_dk = df.coding.str.contains('^9+ "Don\'t Know"').fillna(False)
    df.loc[num_with_dk, 'type'] = 'numeric'

    # These regexs are designned to NOT match the string '[specify unit]',
    # which is a numeric encoding of the unit
    freetext_re = 'specified|, specify|from the certificate|Record from where'
    df.loc[df.question.str.contains(freetext_re), 'type'] = 'freetext'

    # This columns is not actually in the data
    df.drop('gs_diagnosis', inplace=True)

    # The codebook is missing a space between the 1 and "Grams" which causes
    # the mapping from coding function to fail
    df.loc['c1_08a', 'coding'] = ('1 "Grams" 8 "Refused to Answer" '
                                  '9 "Don\'t Know"')

    # The codebook does not mention that the values 9999 is used as a sentinel
    # for missing for child weight at previous medical visits
    df.loc[['c5_07_1', 'c5_07_2'], 'coding'] = '9999 "Don\'t Know"'

    df.rename(columns={'health_care_experience': 'hce'}, inplace=True)
    order = ['question', 'module', 'type', 'hce', 'coding']

    return df[order]


def recode_ghdx_data(df, codebook):
    """Recode the values of columns to match the codebook.

    This function:
        * creates and sets a unique index across all files by concatenting
          ``module`` and ``newid``
        * recodes categorical variable from their label to their encoded value
        * replaces string missing labels with ``float('nan')``
        * recodes word columns from counts of occurences to binary flags

    Args:
        df (dataframe): a single module of raw GHDx data
        codebook (dataframe): cleaned GHDx codebook

    Returns:
        (dataframe)
    """
    # Create an string identifier which is unique across all observations
    df['sid'] = df.module + df.newid.astype(str)
    df = df.set_index('sid')

    cat_cols = codebook[codebook.type == 'categorical'].index
    for col in cat_cols.intersection(df.columns):
        # Codebook entries have the form: '# "text" # "text" ... # "text"'
        # Some entries contain numbers in the values so only digits followed
        # by a space and a double quote should be used as encoded values
        coding_str = codebook.at[col, 'coding']
        coding = dict(zip(re.findall('(?<= ").+?(?=")', coding_str),
                          map(int, re.findall('\d+(?= ")', coding_str))))
        df[col] = pd.to_numeric(df[col].map(coding))

    # Some numeric columns contain the string "Don't Know". These columns
    # were imported as object dtype instead of numeric. Force to numeric
    # replacing DK with missing
    num_cols = codebook[codebook.type == 'numeric'].index
    num_cols = num_cols.intersection(df.columns)
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')

    # Word columns contain frequencies. Change them to indicators.
    word_cols = df.filter(like="word_").columns
    df[word_cols] = df[word_cols].applymap(lambda x: int(x > 0))

    return df


def fix_ghdx_ages(df):
    """Fix inconsistency in the age variables.

    Some entries of age variables are very obvious transcription errors. These
    lead to misclassifying an observation into the wrong age-specific module.
    This analysis is using g5_04 set of variable to calculate age instead of
    the g1_07 used by the original authors. The g1_07 series were ages
    collected from medical records whereas the g5_04 series are responses from
    respondents and better reflect the quality of information available from
    a verbal autopsy interview.

    For discussion on the discrepancies between various methods in calculating
    age for records in the PHMRC dataset see the review of the dataset by
    Byass [byass]_.

    Args:
        df (dataframe): GHDx data.

    Returns:
        (dataframe): the same dataframe is returned with inplace modifications.
    """
    idx = df.index.intersection(['Adult3138', 'Adult7459'])
    df.loc[idx, 'g5_04a'] = df.loc[idx, 'g5_04c']
    df.loc[idx, 'g5_04c'] = float('nan')

    idx = df.index.intersection(['Child954', 'Child1301', 'Child1329'])
    df.loc[idx, 'g5_04b'] = df.loc[idx, 'g5_04a']
    df.loc[idx, 'g5_04a'] = float('nan')

    idx = df.index.intersection(['Child1372'])
    df.loc[idx, 'g5_04c'] = 29

    idx = df.index.intersection(['Child2062'])
    df.drop(idx, inplace=True)

    idx = df.index.intersection(['Neonate545', 'Neonate2152'])
    df.loc[idx, 'g5_04c'] = df.loc[idx, 'g5_04a']
    df.loc[idx, 'g5_04a'] = float('nan')

    idx = df.index.intersection(['Neonate1192', 'Neonate1377'])
    df.loc[idx, 'g5_04c'] = df.loc[idx, 'g5_04b']
    df.loc[idx, 'g5_04b'] = float('nan')

    return df


def fix_ghdx_pox(df):
    """Fix the word pox by recoding it to rash.

    The version of the survey instrument fielded in Udar Pradesh clearly
    mistranslated the word pox to something very close to the rash. At other
    sites the translations of the word pox and rash were not adequate to
    distinguish the two words. The GHDx child data contains 15 endorsements
    for the word pox, 13 for Udar Pradesh and 2 from Bohol. These should all
    be recoded to the word rash.

    Args:
        df (dataframe): GHDx data.

    Returns:
        (dataframe): the same dataframe is returned with inplace modifications.
    """
    if 'word_pox' in df:
        df.word_rash = (df.word_rash + df.word_pox).map(lambda x: int(x > 0))
        df.drop('word_pox', axis=1, inplace=True)
    return df


def fix_ghdx_injuries(df):
    """Remove injury endorsement which occured more than 30 days before death.

    The original survey instrument asked the question about injuries in a very
    open ended manner which was interpreted as any injuries ever, as opposed
    to the injuries leading to death. The subsequent analysis dropped injuries
    which occured more than 30 days before death.

    Args:
        df (dataframe): GHDx data.

    Returns:
        (dataframe): the same dataframe is returned with inplace modifications.
    """
    if 'a5_04' in df:
        mask = df.a5_04 > 30
        for col in df.filter(like='a5_').columns:
            df.loc[mask & df[col].notnull(), col] = 0
    if 'c4_49' in df:
        mask = df.c4_49 > 30
        for col in df.filter(regex='c4_47_|c4_48|c4_49').columns:
            df.loc[mask & df[col].notnull(), col] = 0
    return df


def fix_ghdx_birth_weights(df):
    """Ensure the child birth weight is in grams and is a legal value.

    The original survey allowed answers to weights to be coded in grams or
    kilograms. The GHDx data has recoded the values into grams. However, a
    few cases are clearly still coded in kilograms. The survey also used the
    value 9999 as a sentinel for missing weight in grams. The updated survey
    instrument allows child birth weights between 0.5 kg and 8 kg. We will
    use this as the valid range.

    Args:
        df (dataframe): GHDx data.

    Returns:
        (dataframe): the same dataframe is returned with inplace modifications.
    """
    if 'c1_08b' in df:
        df.loc[df.c1_08b <= 8, 'c1_08b'] = df.c1_08b * 1000   # g => kg
        df.loc[(df.c1_08b > 8) & (df.c1_08b < 500), 'c1_08b'] = float('nan')
    return df


def set_missing_durations(df, codebook):
    duration_rows = codebook.question.str.contains('\[specify units\]')
    durations = codebook.loc[duration_rows].index.str.slice(0, 5)
    cols = df.columns.intersection(durations)
    df[cols] = df[cols].replace(0, float('nan'))
    return df


def clean_ghdx_files():
    """Clean and save all the GHDx files.

    See Also:

        * clean_codebook
        * recode_ghdx_data
        * fix_ghdx_ages
        * fix_ghdx_pox
        * fix_ghdx_injuries
        * fix_ghdx_birth_weights
    """
    try:
        os.mkdir(CLEANED_DATA_DIR)
    except OSError:
        pass   # folder already exists

    print('Cleaning codebook...', end='')
    sys.stdout.flush()
    codebook = clean_codebook(load_ghdx_data('codebook'))
    codebook.to_csv(os.path.join(CLEANED_DATA_DIR, 'ghdx_codebook.csv'),
                    encoding='utf-8')
    print(' done')

    for module in ['adult', 'child', 'neonate']:
        print('Recoding the {} GHDx file...'.format(module), end='')
        sys.stdout.flush()
        df = recode_ghdx_data(load_ghdx_data(module), codebook)
        df = fix_ghdx_ages(df)
        df = fix_ghdx_pox(df)
        df = fix_ghdx_injuries(df)
        df = fix_ghdx_birth_weights(df)
        df = set_missing_durations(df, codebook)
        df.to_csv(os.path.join(CLEANED_DATA_DIR, 'ghdx_{}.csv'.format(module)),
                  encoding='utf-8')
        print(' done')

    print('Files are saved in {}'.format(CLEANED_DATA_DIR))


def load_cleaned_file(module):
    """Load the cleaned GHDX files.

    Args:
        module (str): 'adult', 'child', 'neonate' or 'codebook'

    Returns:
        (dataframe)
    """
    file_ = os.path.join(CLEANED_DATA_DIR, 'ghdx_{}.csv'.format(module))
    with filter_DtypeWarnnings():
        return pd.read_csv(file_, index_col=0, encoding='utf-8')


if __name__ == '__main__':
    clean_ghdx_files()
