from pathlib import Path

import pandas as pd

from cause_specific_results import OUTPUT_FILE as INPUT_FILE, REPO_DIR


def prep_icds():
    icd_file = REPO_DIR / 'results/icd_codes.csv'
    icds = pd.read_csv(icd_file)
    icds.module = icds.module.str.title()
    icds.cause = icds.cause.replace({
        'Homicide (assult)': 'Homicide',
        'Cervical Cancers': 'Cervical Cancer',
        'Poisonings (accidental)': 'Poisonings',
        'Renal Failure (due to renal disease)': 'Renal Failure',
        'Suicide (intentional self-harm)': 'Suicide',
        'Cancers': 'Other Cancers',
        'Cardiovascular Diseases': 'Other Cardiovascular Diseases',
        'Digestive Diseases': 'Other Digestive Diseases',
    })
    icds = icds.set_index(['module', 'cause']).icd.str.replace('*', '') \
               .groupby(level='module').apply(lambda x: x.sort_values())
    icds.index = icds.index.droplevel(0)
    return icds


def sensitivity_specificity_table(df, icds):
    df = df.loc[~df.metric.str.contains('CCC')] \
           .set_index(['module', 'ICD10', 'cause', 'clf', 'hce', 'metric']) \
           .drop('pts', axis=1) \
           .unstack('clf').unstack('hce').unstack('metric')
    df.columns = df.columns.droplevel(0)

    metric_order = ['Median Sensitivity', 'UI Sensitivity',
                    'Median Specificity', 'UI Specificity']
    df = df.reindex(columns=metric_order, level=2)

    # df[('ICD', '', '')] = icds
    clf_order = ['ICD', 'Insilico (Tariff 2.0 Training)', 'Tariff']
    df = df.reindex(columns=clf_order, level=0)

    df.rename_axis(['', '', ''], axis=1) \
      .to_excel(str(REPO_DIR / 'paper/additional_file_5_sensitivity_specificity.xlsx'))


def ccc_table(df, icds):
    df = df.loc[df.metric.str.contains('CCC')].copy()
    df.metric = df.metric.replace({'Median CCC': 'Median', 'UI CCC': '95% UI'})
    df = df.set_index(['module', 'ICD10', 'cause', 'clf', 'hce', 'metric']) \
           .drop('pts', axis=1) \
           .unstack('clf').unstack('hce').unstack('metric')
    df.columns = df.columns.droplevel(0)
    df = df.reindex(columns=['No HCE', 'HCE'], level=1) \
           .reindex(columns=['Median', '95% UI'], level=2)
    df.rename_axis(['', '', ''], axis=1) \
      .to_excel(str(REPO_DIR / 'results/ccc.xlsx'))


def raw_csmf_accuracy_table():
    tariff = pd.read_csv(REPO_DIR / 'results/tariff_performance.csv')
    df = pd.concat([
        pd.read_csv(REPO_DIR / 'results/insilico_performance.csv'),
        tariff.loc[tariff.analysis == 'tariff_2']
    ])
    df.module = df.module.str.title()
    df.hce = df.hce.map({'no_hce': 'No HCE', 'w_hce': 'HCE'})
    df.measure = df.measure.replace({
        'cccsmf_accuracy': 'CCCSMF Accuracy',
        'csmf_accuracy': 'CSMF Accuracy',
        'mean_ccc': 'CCC',
    })
    df.analysis = df.analysis.replace({
        'default_insilico': 'InsilicoVA (Default Probbase)',
        'insilico_insilico': 'InsilicoVA (InterVA training)',
        'phmrc_tariff': 'InSilicoVA (Tariff 2.0 training)',
        'tariff_2': 'Tariff 2.0',
    })
    df = df.set_index(['analysis', 'module', 'hce', 'measure']).round(1)
    df['UI 95%'] = '(' + df.lb.astype(str) + ', ' + df.ub.astype(str) + ')'
    df['Median'] = df.value
    df = df[['Median', 'UI 95%']].copy()
    df.columns.name = 'value'
    df.stack().unstack('analysis').unstack('hce').unstack('value') \
      .rename_axis(['', '', ''], axis=1).rename_axis(['', ''], axis=0) \
      .to_excel(str(REPO_DIR / 'results/insilico_performance.xlsx'))


def main():
    icds = prep_icds()
    stats = ['sensitivity', 'specificity', 'ccc']
    df = pd.read_csv(INPUT_FILE, index_col=[0, 1], header=[0, 1, 2, 3]) \
           .loc[:, pd.IndexSlice[:, :, stats, :]] \
           .stack('clf').stack('hce').stack('metric') \
           .assign(UI=lambda x:
                '(' + x.lb.astype(str) + ', ' + x.ub.astype(str) + ')') \
           .drop(['lb', 'ub'], axis=1).stack().rename('value').reset_index()

    df.module = df.module.str.title()
    df.hce = df.hce.map({'True': 'HCE', 'False': 'No HCE'})
    df.pts = df.pts.replace('med', 'Median')
    df.metric = df.pts + ' ' + df.metric.str.title().replace('Ccc', 'CCC')
    df.clf = df.clf.replace('Insilico', 'Insilico (Tariff 2.0 Training)')
    df['ICD10'] = df.apply(lambda x: icds.loc[(x.module, x.cause)], axis=1)

    ccc_table(df, icds)
    sensitivity_specificity_table(df, icds)
    raw_csmf_accuracy_table()


if __name__ == '__main__':
    main()
