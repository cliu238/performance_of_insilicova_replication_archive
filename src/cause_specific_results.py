from pathlib import Path

import pandas as pd
import numpy as np

from prep import REPO_DIR
import metrics


REPO_DIR = Path(REPO_DIR)
INPUT_DIR = REPO_DIR / 'data/results_phmrc_tariff'
OUTPUT_FILE = REPO_DIR / 'data/table1.csv'

def read_tariff_performance():
    """Read and format tariff results from the horserace paper.

    Published estimates of sensitivity and specificity can be found in
    appendix 8 of the horserace paper available from:
    https://bmcmedicine.biomedcentral.com/articles/10.1186/1741-7015-12-5
    """
    files = [
        REPO_DIR / 'results/tariff_sensitivity_specificity.csv',
        REPO_DIR / 'results/tariff_ccc_by_cause.csv'
    ]
    dfs = [
        pd.read_csv(f, index_col=[0, 1], header=[0, 1, 2])
           .rename_axis(['module', 'cause'], axis='index')
           .rename_axis(['clf', 'hce', 'metric'], axis='columns')
           .stack('clf').stack('hce')
           .reset_index('hce')
           .assign(hce=lambda x: ~x.hce.str.startswith('No'))
           .set_index('hce', append=True)
        for f in files
    ]

    sens_spec, ccc = dfs

    # Align ccc with sens_spec
    ccc = ccc.reset_index('clf').assign(clf='Tariff')\
             .set_index('clf', append=True).swaplevel(3, 2)

    cols = pd.MultiIndex.from_product([
        ['sensitivity', 'specificity', 'ccc'], ['lb', 'med', 'ub']])
    out = pd.DataFrame(index=sens_spec.index, columns=cols)

    out[('sensitivity', 'med')] = sens_spec['Median Sensitivity']
    out[('specificity', 'med')] = sens_spec['Median Specificity']
    out[('ccc', 'med')] = ccc['Median (%)']

    ui_re = r'^\((\d{1,3}\.\d),\s(\d{1,3}\.\d)\)$'   # hehehe
    out[[('sensitivity', 'lb'), ('sensitivity', 'ub')]] = \
        sens_spec['UI Sensitivity'].str.extract(ui_re, expand=True)
    out[[('specificity', 'lb'), ('specificity', 'ub')]] = \
        sens_spec['UI Specificity'].str.extract(ui_re, expand=True)
    out[[('ccc', 'lb'), ('ccc', 'ub')]] = \
        ccc['95% CI'].str.extract(ui_re, expand=True)

    return out.astype(float).rename_axis(['metric', 'pts'], axis=1) \
              .stack().stack() \
              .unstack('clf').unstack('hce').unstack('metric').unstack('pts')


def calc_stats(df):
    stats = (metrics.calc_sensitivity, metrics.calc_specificity,
             metrics.calc_ccc)
    return pd.concat([
        pd.Series({cause: metric(cause, df.actual, df.prediction)
                   for cause in df.actual.unique()},
                  name=metric.__name__.split('_')[-1])
        for metric in stats
    ], axis=1)


def calc_median_and_ui_(df):
    pts = ('med', 'lb', 'ub')
    out = []
    rs = np.random.RandomState(8675309)
    for col in df.columns:
        med, (lb, ub) = metrics.calc_median_and_ui(df[col], random_state=rs)
        out.append(pd.Series([med, lb, ub], pts, name=col))

    return pd.concat(out, axis=1).stack().swaplevel().sort_index() \
             .rename_axis(['metric', 'pts']).rename('value')


def summarize(module, hce):
    hce_ = 'w_hce' if hce else 'no_hce'
    filename = 'validate_insilico_{}_{}_phmrc_tariff_predictions.csv'.format(
        module, hce_)
    df = pd.read_csv(INPUT_DIR / filename)
    if 'split' not in df.columns:
        df['split'] = np.repeat(np.arange(500), df.shape[0] / 500)

    stats = df.groupby('split').apply(calc_stats) \
              .groupby(level=1).apply(calc_median_and_ui_) \
              .mul(100).round(1)
    stats.loc[:, ('prediction', 'all')] = df.prediction.value_counts() \
                                            .fillna(0).astype(int)
    stats.loc[:, ('actual', 'all')] = df.actual.value_counts() \
                                        .fillna(0).astype(int)

    return stats


def main():
    tariff = read_tariff_performance()
    insilicio = pd.concat([
        summarize(module, hce).assign(module=module, hce=hce)
        for module in ('adult', 'child', 'neonate') for hce in (True, False)
    ]).assign(clf='Insilico') \
      .set_index(['clf', 'module', 'hce'], append=True) \
      .stack().stack() \
      .unstack('clf').unstack('hce').unstack('metric').unstack('pts') \
      .T.dropna().T \
      .swaplevel().sort_index() \
      .rename_axis(['module', 'cause'])
    pd.concat([insilicio, tariff], axis=1).to_csv(OUTPUT_FILE)


if __name__ == '__main__':
    main()
