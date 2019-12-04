from __future__ import print_function
import contextlib
import os
import warnings

import pandas as pd


REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GHDX_CODEBOOK = 'IHME_PHMRC_VA_DATA_CODEBOOK_Y2013M09D11_0.csv'
GHDX_FILENAME = 'IHME_PHMRC_VA_DATA_{}_Y2013M09D11_0.csv'
GHDX_DATA_DIR = os.path.join(REPO_DIR, 'data', 'ghdx')


@contextlib.contextmanager
def filter_DtypeWarnnings():
    warnings.simplefilter('ignore', pd.io.common.DtypeWarning)
    try:
        yield
    finally:
        warnings.resetwarnings()


def download_ghdx_data():
    """Download PHMRC data and codebook from GHDx.

    This study uses the Population Health Metrics Research Consortium (PHMRC)
    Gold Standard Verbal Autopsy dataset [phmrc]_. This dataset is freely
    available online from the Global Health Data Exchange (GHDx) [ghdx]_.

    Data and codebook are saved with the original names in {REPO}/data/ghdx.
    The original codebook file from the GHDx is an excel file, but it is saved
    as a csv.

    Returns:
        codebook (dataframe)
        adult_data (dataframe)
        child_data (dataframe)
        neonate_data (dataframe)
    """
    try:
        os.mkdir(GHDX_DATA_DIR)
    except OSError:
        pass   # folder already exists

    out = []
    ghdx_url = ('http://ghdx.healthdata.org/sites/default/files/'
                'record-attached-files')

    url = '{ghdx}/{cb}.xlsx'.format(ghdx=ghdx_url, cb=GHDX_CODEBOOK[:-4])
    print('Downloading: {}'.format(url))
    codebook = pd.read_excel(url, encoding='latin-1')
    filepath = os.path.join(GHDX_DATA_DIR, GHDX_CODEBOOK)
    codebook.to_csv(filepath, encoding='utf-8', index=False)
    out.append(codebook)

    for module in ['ADULT', 'CHILD', 'NEONATE']:
        filename = GHDX_FILENAME.format(module)
        url = '{ghdx}/{f}'.format(ghdx=ghdx_url, f=filename)
        print('Downloading: {}'.format(url))
        with filter_DtypeWarnnings():
            df = pd.read_csv(url, encoding='latin-1')
        filepath = os.path.join(GHDX_DATA_DIR, filename)
        df.to_csv(filepath, index=False, encoding='utf-8')
        out.append(df)
    print('Files are saved in {}'.format(GHDX_DATA_DIR))

    return tuple(out)


def load_ghdx_data(module):
    """Load the saved GHDX files.

    Args:
        module (str): 'adult', 'child', 'neonate' or 'codebook'

    Returns:
        (dataframe)
    """
    module = module.upper()
    if module == 'CODEBOOK':
        filename = GHDX_CODEBOOK
    elif module in ['ADULT', 'CHILD', 'NEONATE']:
        filename = GHDX_FILENAME.format(module)
    else:
        raise ValueError('Unknown module: "{}"'.format(module))
    filepath = os.path.join(GHDX_DATA_DIR, filename)
    with filter_DtypeWarnnings():
        return pd.read_csv(filepath, encoding='utf-8')


if __name__ == '__main__':
    download_ghdx_data()
