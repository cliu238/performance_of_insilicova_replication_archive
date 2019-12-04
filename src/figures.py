from itertools import product
import os
import sys

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
import seaborn as sns

from results import load_results
from paper import PAPER_DIR
from cause_specific_results import INPUT_DIR, REPO_DIR
from annex_tables import prep_icds

sns.set()


OUTPUT_DIR = REPO_DIR / 'paper/figures'


def format_results(df):
    keep = (df.measure.isin(['mean_ccc', 'cccsmf_accuracy']) &
            df.analysis.isin(['default_insilico', 'insilico_insilico',
                              'phmrc_tariff', 'tariff_2']))
    return df.loc[keep].set_index(['module', 'hce', 'analysis', 'measure']) \
             .stack().unstack(-2).unstack()


def path(x_lb, x_ub, y_lb, y_ub, **_):
    c = 4
    verts = [
        (x_lb, 0),
        (x_lb / c, y_ub / c),
        (0, y_ub),
        (x_ub / c, y_ub / c),
        (x_ub, 0),
        (x_ub / c, y_lb / c),
        (0, y_lb),
        (x_lb / c, y_lb / c),
        (x_lb, 0),
    ]
    codes = np.full(9, Path.CURVE3)
    codes[0] = Path.MOVETO
    codes[-1] - Path.CLOSEPOLY
    return Path(verts, codes, closed=True)


def horserace_plot(df):
    fig, axs = plt.subplots(nrows=2, ncols=3, sharex=True, sharey=True)
    fig.set_size_inches(8, 6)   # in inches
    fig.set_tight_layout({'h_pad': .1, 'w_pad': -.7})

    modules = ('adult', 'child', 'neonate')
    hces = ('w_hce', 'no_hce')
    hce_names = {'w_hce': 'HCE', 'no_hce': 'No HCE'}
    labels = {
        'default_insilico': 'InSilicoVA (default)',
        'insilico_insilico': 'InSilicoVA (InterVA)',
        'phmrc_tariff': 'InSilicoVA (Tariff)',
        'tariff_1': 'Tariff 1.0',
        'tariff_2': 'Tariff 2.0',
        'tariff_2_short': 'Tariff 2.0 (short)',
        'smartva_full': 'SmartVA (full)',
        'smartva_short': 'SmartVA (short)',
    }
    x_header = 'cccsmf_accuracy'
    y_header = 'mean_ccc'
    val_header = 'value'
    ui_headers = ['lb', 'ub']

    for (j, module), (i, hce) in product(enumerate(modules), enumerate(hces)):
        ax = axs[i, j]

        idx = (module, hce)
        x = df.loc[idx, (x_header, val_header)]
        y = df.loc[idx, (y_header, val_header)]
        x_ui = df.loc[idx, x_header][ui_headers]
        y_ui = df.loc[idx, y_header][ui_headers]

        ax.set_title('{}-{}'.format(module.title(), hce_names[hce]))

        # Add xlabel only on the bottom plots
        if i == 1:
            ax.set_xlabel('Chance-corrected CSMF Accuracy', fontsize=10)

        # Add ylabel only on left most plots
        if j == 0:
            ax.set_ylabel('Chance-corrected Concordance', fontsize=10)

        d = pd.concat([x, y, x_ui.sub(x, axis=0), y_ui.sub(y, axis=0)], axis=1)
        d.columns = ['x', 'y', 'x_lb', 'x_ub', 'y_lb', 'y_ub']
        d.index = d.index.map(labels.get)

        # Add scatter symbols
        for i, row in d.iterrows():
            ax.plot(row.x, row.y, marker='.', color='black')

        # Label scattered points. Manually adjust labels
        for analysis in df.loc[idx].index:
            label_x = x.loc[analysis]
            label_y = y.loc[analysis] - 0.7
            label = labels.get(analysis, analysis)
            if label == 'Tariff 2.0':
                label_x -= 32
            elif label == 'InSilicoVA (Tariff)':
                label_x -= 57
            elif label == 'InSilicoVA (InterVA)':
                label_x -= 65
            elif label == 'InSilicoVA (default)':
                label_x += 4

            if hce == 'w_hce':
                if module == 'adult':
                    if label == 'InSilicoVA (Tariff)':
                        label_y += 0.5
                    if label == 'InSilicoVA (InterVA)':
                        label_y -= 0.5
                if module == 'child':
                    if label == 'InSilicoVA (InterVA)':
                        label_x = x.loc[analysis] + 3
                        label_y = y.loc[analysis] - 0.7
            elif hce == 'no_hce':
                if module == 'adult':
                    if label == 'InSilicoVA (Tariff)':
                        label_x = x.loc[analysis] + 4.5
                        label_y = y.loc[analysis]
                    if label == 'InSilicoVA (InterVA)':
                        label_y -= .5
                        label_x -= 1
                if module == 'child':
                    if label == 'InSilicoVA (InterVA)':
                        label_x = x.loc[analysis] + 3
                        label_y = y.loc[analysis] - 0.7

            ax.annotate(label, xy=(label_x, label_y), fontsize=8)

    return fig

def plot_all_heatmaps():
    for hce in (True, False):
        for module in ('adult', 'child', 'neonate'):
            fig = plot_heatmap(module, hce)
            filename = 'heatmap_{}_hce{}.png'.format(module, int(hce))
            fig.savefig(str(OUTPUT_DIR / filename))
            fig.savefig(str(OUTPUT_DIR / filename.replace('.png', '.pdf')))


def plot_heatmap(module, hce):
    # import pdb; pdb.set_trace()
    icds = prep_icds().loc[module.title()].sort_values()
    filename = 'validate_insilico_{}_{}_phmrc_tariff_predictions.csv'
    hce_ = 'w_hce' if hce else 'no_hce'
    df = pd.read_csv(INPUT_DIR / filename.format(module, hce_))

    data = pd.crosstab(
        df.actual.rename('True Cause'),
        df.prediction.rename('Predicted Cause'),
        margins=True)
    causes = data.index.intersection(data.columns).tolist()
    causes.remove('All')
    causes.sort(key=icds.index.tolist().index)
    causes.append('All')
    data = data.loc[causes, causes].fillna(0)
    labels = {cause: '{} ({})'.format(cause, icd)
              for cause, icd in icds.iteritems()}
    labels['All'] = 'All'
    data.index = data.index.map(labels.get)
    data.columns = data.columns.map(labels.get)

    table_num = {'adult': 2, 'child': 3, 'neonate': 4}
    outdir = REPO_DIR / 'data/heatmaps'
    outdir.mkdir(parents=True, exist_ok=True)
    data.to_csv(outdir / '{}_hce{:d}.csv'.format(module, hce))

    filename = 'additional_file_{}_{}_misclassification_matrix.xlsx'
    data.to_excel(str(REPO_DIR / 'paper' /
                      filename.format(table_num[module], module)))
    data.stack().rename_axis(['True Cause', 'Predicted Cause']).rename('N') \
        .to_csv(outdir / '{}_hce{:d}_long.csv'.format(module, hce),
                header=True)

    with sns.plotting_context('paper'):
        fig, ax = plt.subplots(figsize=(15, 12))
        cmap = sns.color_palette('Blues', n_colors=20)
        sns.heatmap(data, ax=ax, cmap=cmap, annot=True,
                    annot_kws={'fontsize': 6}, fmt=',d')
        plt.tight_layout()
        plt.subplots_adjust(top=.95)
        ax.set_title(module.title())
    return fig


def main():
    plot_all_heatmaps()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print('Graphing results...', end='')
    sys.stdout.flush()
    df = load_results()
    df = format_results(df)

    fig = horserace_plot(df)
    path = os.path.join(PAPER_DIR, 'figures', 'horserace.png')
    fig.savefig(path)
    fig.savefig(path.replace('.png', '.pdf'))
    print(' done.')


if __name__ == '__main__':
    main()
