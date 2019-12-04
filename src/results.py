from __future__ import print_function
from collections import OrderedDict
from itertools import product
import glob
import os
import sys

import pandas as pd
import numpy as np
import yaml

from download import REPO_DIR, load_ghdx_data
from map_insilico import INSILICO_CAUSE_MAP, INSILICO_SYMPTOM_MAP
from map_tariff import TARIFF_SYMPTOM_MAP
from metrics import calc_median_and_ui
from paper import PAPER_DIR, TABLES


MODULES = ('adult', 'child', 'neonate')
HCES = ('no_hce', 'w_hce')
RESULTS_DIR = os.path.join(REPO_DIR, 'results')


def represent_ordereddict(dumper, data):
    """From: https://stackoverflow.com/questions/16782112/
             can-pyyaml-dump-dict-items-in-non-alphabetical-order
    """
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)


yaml.add_representer(OrderedDict, represent_ordereddict)


def get_methods_numbers():
    num = OrderedDict()

    ghdx = {module: load_ghdx_data(module) for module in MODULES}
    stillbirths = ghdx['neonate'].gs_text34 == 'Stillbirth'

    num['n_records'] = format(sum([len(df) for df in ghdx.values()]), ',')
    num['n_adult'] = format(len(ghdx['adult']), ',')
    num['n_child'] = format(len(ghdx['child']), ',')
    num['n_neonate'] = format(len(ghdx['neonate'].loc[~stillbirths]), ',')
    num['n_stillbirth'] = format(len(ghdx['neonate'].loc[stillbirths]), ',')

    for module in MODULES:
        n_causes_key = 'n_{}_causes'.format(module)
        num[n_causes_key] = len(set(INSILICO_CAUSE_MAP[module].values()))

        insilico_symptoms = [symp[0] for symp in INSILICO_SYMPTOM_MAP[module]
                             if symp[1] is not None]
        num['n_{}_i_symptoms'.format(module)] = len(insilico_symptoms)

        num['n_{}_t_symptoms'.format(module)] = len(TARIFF_SYMPTOM_MAP[module])

    hyperparams = ['updateCondProb', 'keepProbbase.level', 'Nsim', 'thin',
                   'burnin', 'auto.length', 'conf.csmf', 'jump.scale',
                   'levels.prior', 'levels.strength']
    num['n_hyperparam'] = len(hyperparams)

    return num


def load_insilico_output_by_splits():
    data_dir = os.path.join(REPO_DIR, 'data')
    analyses = {
        'results_default_insilico': ('default', ''),
        'results_insilico_insilico': ('validate', 'insilico_insilico_'),
        'results_phmrc_tariff': ('validate', 'phmrc_tariff_'),
    }

    results = []
    for subdir, (analysis, file_tag) in analyses.items():
        for module in MODULES:
            for hce in ['w_hce', 'no_hce']:
                filename = '{}_insilico_{}_{}_{}accuracy.csv'.format(
                    analysis, module, hce, file_tag)
                df = pd.read_csv(os.path.join(data_dir, subdir, filename))
                df['hce'] = hce
                df['analysis'] = subdir[len('results_'):]
                df['module'] = module
                results.append(df)
    return pd.concat(results)


def get_extended_convergence_data():
    pattern = os.path.join(REPO_DIR, 'data', 'results_*_ext',
                           '*accuracy.csv')
    return [pd.read_csv(f).converged.mean() for f in glob.glob(pattern)]


def get_point_estimate_with_ui(series, random_state=None):
    med, (lb, ub) = calc_median_and_ui(series, random_state=random_state)
    return pd.Series([med, lb, ub], ['value', 'lb', 'ub'])


def calc_summary_results(df):
    rs = np.random.RandomState(8675309)
    metrics = ['mean_ccc', 'csmf_accuracy', 'cccsmf_accuracy']

    # Convert proportions to percents
    df[metrics] = df[metrics] * 100

    df = df.set_index(['analysis', 'module', 'hce', 'split'])[metrics].stack()
    df.index.rename('measure', level=-1, inplace=True)
    df.name = 'value'

    # Grouped across splits
    return df.reset_index().groupby(['analysis', 'module', 'hce', 'measure']) \
             .value.apply(get_point_estimate_with_ui, random_state=rs) \
             .unstack()


def format_median_and_ui(series):
    med, lb, ub = series.loc[['value', 'lb', 'ub']]
    return pd.Series([format(med, '.1f'), '({:.1f}, {:.1f})'.format(lb, ub)],
                     ['Median', '95% UI'])


def format_table_numbers(df, analyses):
    data = OrderedDict()
    data['clfs'] = [analyses[clf]
                    for clf in df.index.get_level_values('analysis').unique()
                    if clf in analyses]
    for module, hce in product(MODULES, HCES):
        values = df.loc[pd.IndexSlice[analyses.keys(), module, hce, :], :] \
                   .to_dict('split')['data']
        data['{}_{}'.format(module, hce)] = values

    return data

def pct(x):
    return '{:.1f}%'.format(x)


def get_results_numbers(results, df, tariff2):
    idx = pd.IndexSlice

    num = OrderedDict()
    num['table_ccc'] = TABLES.index('table_ccc') + 1

    analyses = OrderedDict([
        ('tariff', 'phmrc_tariff'),
        ('default', 'default_insilico'),
        ('insilico', 'insilico_insilico'),
    ])
    measures = OrderedDict([
        ('ccc', 'mean_ccc'),
        ('cccsmf', 'cccsmf_accuracy'),
    ])

    combos = product(MODULES, analyses.items(), measures.items())
    for module, (a_short, a_full), (m_short, m_full) in combos:
        key = '{}_{}_{}'.format(a_short, module, m_short)
        idx = (a_full, module, 'no_hce', m_full)
        num[key] = df.loc[idx].map(pct).to_dict()

    num['table_cccsmf'] = TABLES.index('table_cccsmf') + 1

    for module, (m_short, m_full) in product(MODULES, measures.items()):
        insilico = df.loc[('phmrc_tariff', module, 'no_hce', m_full), 'value']
        tariff = tariff2.loc[('tariff_2', module, 'no_hce', m_full), 'value']
        key = 'diff_{}_{}'.format(module, m_short)
        num[key] = format(tariff - insilico, '.1f')

    convergence = results.groupby(['analysis', 'module', 'hce']) \
                         .converged.mean() \
                         .drop('default_insilico')
    num['pct_unconverged_lower'] = pct(100 - convergence.min() * 100)
    num['pct_unconverged_upper'] = pct(100 - convergence.max() * 100)

    ext_data = get_extended_convergence_data()
    num['pct_unconverged_lower_ext'] = pct(100 - min(*ext_data) * 100)
    num['pct_unconverged_upper_ext'] = pct(100 - max(*ext_data) * 100)

    insilico_key = 'Insilico (Tariff 2.0 Training)'
    hce = 'No HCE'

    ccc = load_cause_specific_ccc_results()
    insilico_col = (insilico_key, hce, 'Median')
    highest_ccc = ccc[insilico_col].groupby(level='module').nlargest(3)
    for module in MODULES:
        num['{}_high_ccc_causes'.format(module)] = sorted(
            highest_ccc.loc[module.title()].index.get_level_values('cause')
        )

    ccc_lb = ccc[(insilico_key, hce, '95% UI')].str.extract('^\((-?\d+\.\d),')
    num['n_rand_ccc'] = int(ccc_lb.astype(float).le(0).sum())

    ccc_higher = ccc.loc[ccc[insilico_col] > ccc[('Tariff', hce, 'Median')]]
    for module in MODULES:
        num['higher_ccc_{}'.format(module)] = sorted(
            ccc_higher.loc[module.title()].index.get_level_values('cause')
        )

    sens_spec = load_sens_spec_results()
    num['n_phmrc_causes'] = int(sens_spec.shape[0])
    for metric in ('Sensitivity', 'Specificity'):
        key = 'n_insilico_higher_{}'.format(metric.lower()[:4])
        key_col = 'Median {}'.format(metric)
        col_insilico = (insilico_key, hce, key_col)
        col_tariff = ('Tariff', hce, key_col)
        gt = sens_spec[(col_insilico)] > sens_spec[col_tariff]
        num[key] = int((gt).sum())

    num['table_adult_ccc'] = TABLES.index('table_adult_ccc') + 1
    num['table_neonate_ccc'] = TABLES.index('table_neonate_ccc') + 1
    return num

def get_abstract_numbers(summary, results):
    df = summary.loc[pd.IndexSlice[:, :, :, 'cccsmf_accuracy'], 'value'] \
                .groupby(level='analysis').agg(['min', 'max'])
    analyses = {
        'default_insilico': 'default',
        'insilico_insilico': 'insilico',
        'phmrc_tariff': 'tariff',
    }
    num = OrderedDict()

    for a, (min_val, max_val) in df.iterrows():
        key = analyses.get(a)
        num['{}_min'.format(key)] = pct(min_val)
        num['{}_max'.format(key)] = pct(max_val)

    diff = [results['diff_{}_cccsmf'.format(m)] for m in MODULES]
    num['diff_lower'] = min(diff)
    num['diff_upper'] = max(diff)

    with open(os.path.join(PAPER_DIR, 'metadata.yml')) as f:
        metadata = yaml.load(f)
    num['keywords'] = ', '.join(metadata['keywords'])
    return num


def get_discussion_numbers(results, tariff2):
    insilico_ccc = results.loc[('phmrc_tariff', 'adult', 'no_hce', 'mean_ccc'),
                               'value']
    tariff_ccc = tariff2.loc[('tariff_2', 'adult', 'no_hce', 'mean_ccc'),
                             'value']

    insilico_csmf = results.loc[('phmrc_tariff', 'adult', 'no_hce',
                                 'cccsmf_accuracy'), 'value']
    tariff_csmf = tariff2.loc[('tariff_2', 'adult', 'no_hce',
                               'cccsmf_accuracy'), 'value']

    num = OrderedDict()
    num['diff_adult_ccc'] = format(tariff_ccc - insilico_ccc, '.1f')
    num['diff_adult_csmf'] = format(tariff_csmf - insilico_csmf, '.1f')
    return num


def load_insilico_results():
    return pd.read_csv(os.path.join(RESULTS_DIR, 'insilico_performance.csv'))


def load_tariff_results():
    return pd.read_csv(os.path.join(RESULTS_DIR, 'tariff_performance.csv')) \
             .drop('source', axis=1)


def load_smartva_results():
    return pd.read_csv(os.path.join(RESULTS_DIR,
                                    'smartva-v1.2.0_performance.csv'))


def load_results():
    return pd.concat([
        load_insilico_results(),
        load_tariff_results(),
        load_smartva_results(),
    ])


def load_cause_specific_ccc_results():
    path = os.path.join(RESULTS_DIR, 'ccc.xlsx')
    return pd.read_excel(path, header=[0, 1, 2], index_col=[0, 1, 2])


def load_sens_spec_results():
    path = os.path.join(RESULTS_DIR,
                        'additional_file_5_sensitivity_specificity.xlsx')
    return pd.read_excel(path, header=[0, 1, 2], index_col=[0, 1, 2])


def format_cause_specific_ccc(df, module):
    return {
        'data': [[cause, icd, data.values.tolist()]
                 for (icd, cause), data in df.loc[module.title()].iterrows()],
        'module': module,
    }


def get_sens_spec_numbers():
    df = load_sens_spec_results().rename_axis(['clf', 'hce', 'metric'], axis=1)
    clfs = ('Insilico (Tariff 2.0 Training)', 'Tariff')
    metrics = ('Sensitivity', 'Specificity')
    cols = [(clf, 'Median {}'.format(metric))
            for clf in clfs for metric in metrics]
    table = df.stack('hce')[cols].groupby(['module', 'hce']).mean().round(1)
    return {' '.join(idx).replace(' ', '_').lower(): data.values.tolist()
            for (idx, data) in table.iterrows()}


def main():
    print('Calculating numbers for paper...', end='')
    sys.stdout.flush()

    results = load_insilico_output_by_splits()
    summary = calc_summary_results(results)
    summary.to_csv(os.path.join(RESULTS_DIR, 'insilico_performance.csv'))

    idx_cols = ['analysis', 'module', 'hce', 'measure']
    tariff = load_tariff_results().set_index(idx_cols)
    df = pd.concat([summary, tariff]) \
           .apply(format_median_and_ui, axis=1) \
           .sort_index()

    ccc = pd.read_excel(os.path.join(REPO_DIR, 'results', 'ccc.xlsx'),
                        index_col=[0, 1, 2], header=[0, 1, 2])
    ccc_cols = pd.IndexSlice[:, :, 'Median']
    ccc.loc[:, ccc_cols] = ccc.loc[:, ccc_cols].round(1).astype(str)

    tables_map = {
        'default_insilico': 'InsilicoVA (Default Probbase)',
        'insilico_insilico': 'InsilicoVA (InterVA training)',
        'phmrc_tariff': 'InSilicoVA (Tariff 2.0 training)',
        'tariff_2': 'Tariff 2.0',
    }

    ccc_idx = pd.IndexSlice[:, :, :, 'mean_ccc']
    cccsmf_idx = pd.IndexSlice[:, :, :, 'cccsmf_accuracy']

    nums = {
        'methods': get_methods_numbers(),
        'results': get_results_numbers(results, summary, tariff),
        'discussion': get_discussion_numbers(summary, tariff),
    }
    nums['abstract'] = get_abstract_numbers(summary, nums['results'])
    tables = {
        'ccc': format_table_numbers(df.loc[ccc_idx, :], tables_map),
        'cccsmf': format_table_numbers(df.loc[cccsmf_idx, :], tables_map),
        'adult_ccc': format_cause_specific_ccc(ccc, 'adult'),
        'child_ccc': format_cause_specific_ccc(ccc, 'child'),
        'neonate_ccc': format_cause_specific_ccc(ccc, 'neonate'),
        'sens_spec': get_sens_spec_numbers(),
    }

    outdir = os.path.join(REPO_DIR, 'paper', 'numbers')
    for section, numbers in nums.items():
        with open(os.path.join(outdir, '{}.yml'.format(section)), 'w') as f:
            f.write(yaml.dump(numbers))

    for table, numbers in tables.items():
        numbers['table_num'] = TABLES.index('table_{}'.format(table)) + 1
        filename = os.path.join(outdir, 'table_{}.yml'.format(table))
        with open(filename, 'w') as f:
            f.write(yaml.dump(numbers, default_flow_style=False))
    print(' done')

    print('Files saved in {}'.format(outdir))


if __name__ == '__main__':
    main()
