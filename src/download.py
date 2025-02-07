from __future__ import print_function
import contextlib
import os
import warnings

import pandas as pd
from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GHDX_CODEBOOK = 'IHME_PHMRC_VA_DATA_CODEBOOK_Y2013M09D11_0.csv'
GHDX_FILENAME = 'IHME_PHMRC_VA_DATA_{}_Y2013M09D11_0.csv'
GHDX_DATA_DIR = os.path.join(REPO_DIR, 'data', 'ghdx')


@contextlib.contextmanager
def filter_DtypeWarnnings():
    """Filter out DtypeWarning in pandas (fixed version)."""
    warnings.simplefilter('ignore', pd.errors.DtypeWarning)  # ✅ 修正错误
    try:
        yield
    finally:
        warnings.simplefilter('default', pd.errors.DtypeWarning)  # ✅ 恢复默认行


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
    codebook = pd.read_excel(url)
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


def load_ghdx_data_old(module):
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
    

# Configuration for the SSH tunnel
SSH_CONFIG = {
    'hostname': 'dslogin01.pha.jhu.edu',
    'username': 'cliu238',
    'password': 'Baza7183!',  # Replace with your actual SSH password
}

# Configuration for the database connection
DB_CONFIG = {
    'host': 'naoj01',
    'user': 'eric',
    'database': 'COSMA',
    'password': 'Baza7183!',  # Replace with your actual DB password
}

import pandas as pd
from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine

# SSH configuration for tunneling
SSH_CONFIG = {
    'hostname': 'dslogin01.pha.jhu.edu',
    'username': 'cliu238',
    'password': 'Baza7183!',  # Replace with your actual SSH password
}

# PostgreSQL database configuration
DB_CONFIG = {
    'host': 'naoj01',
    'user': 'eric',
    'database': 'COSMA',
    'password': 'Baza7183!',  # Replace with your actual DB password
}

def load_ghdx_data(module):
    """
    Load the GHDX data from the PostgreSQL database using an SSH tunnel.

    Args:
        module (str): One of 'adult', 'child', 'neonate', or 'codebook'

    Returns:
        pd.DataFrame: Data loaded from the corresponding table.
    """
    module = module.upper()
    if module == 'CODEBOOK':
        table_name = 'ihme_phmrc_va_data_codebook_y2013m09d11_0'
    elif module == 'ADULT':
        table_name = 'ihme_phmrc_va_data_adult_y2013m09d11_1'
    elif module == 'CHILD':
        table_name = 'ihme_phmrc_va_data_child_y2013m09d11_2'
    elif module == 'NEONATE':
        table_name = 'ihme_phmrc_va_data_neonate_y2013m09d11_1'
    else:
        raise ValueError(f'Unknown module: "{module}"')
    
    # Create an SSH tunnel to the remote database host.
    # PostgreSQL typically uses port 5432.
    with SSHTunnelForwarder(
        (SSH_CONFIG['hostname'], 22),
        ssh_username=SSH_CONFIG['username'],
        ssh_password=SSH_CONFIG['password'],
        remote_bind_address=(DB_CONFIG['host'], 5432)
    ) as tunnel:
        local_port = tunnel.local_bind_port
        
        # Construct the SQLAlchemy connection URL for PostgreSQL.
        connection_url = (
            f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@127.0.0.1:{local_port}/{DB_CONFIG['database']}"
        )
        engine = create_engine(connection_url)
        
        # Construct the SQL query. The table is assumed to be in the 'source_phmrc' schema.
        query = f"SELECT * FROM source_phmrc.{table_name}"
        df = pd.read_sql(query, engine)
        print(df)
    return df

if __name__ == '__main__':
     load_ghdx_data('CODEBOOK')
