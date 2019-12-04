import itertools
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parent.parent

modules = ('adult', 'child', 'neonate')
hces = ('w_hce', 'no_hce')
outputs = ('accuracy', 'ccc', 'csmf', 'predictions')


def combine(experiment, symptoms, causes, extended=False):
    results = 'extended' if extended else experiment
    ext = '_ext' if extended else ''
    input_dir = REPO / 'data/{}_{}_{}'.format(results, causes, symptoms)

    if experiment == 'validate':
        output_dir = REPO / 'data/results_{}_{}{}'.format(causes, symptoms, ext)
        input_tmp = '{}_insilico_{}_{}_{}_{}_*_{}.csv'
        output_tmp = '{}_insilico_{}_{}_{}_{}_{}.csv'
    elif experiment == 'default':
        output_dir = REPO / 'data/results_default_insilico{}'.format(ext)
        input_tmp = '{}_insilico_{}_{}_*_{}.csv'
        output_tmp = '{}_insilico_{}_{}_{}.csv'
    else:
        raise ValueError
    output_dir.mkdir(parents=True, exist_ok=True)

    for module, hce, output in itertools.product(modules, hces, outputs):
        tags = [experiment, module, hce]
        if experiment == 'validate':
            tags.extend([causes, symptoms])
        tags.append(output)
        pd.concat([
            pd.read_csv(f) for f in input_dir.glob(input_tmp.format(*tags))
        ]).to_csv(REPO / output_dir / output_tmp.format(*tags), index=False)


if __name__ == '__main__':
    combine('validate', 'tariff', 'phmrc')
    combine('validate', 'insilico', 'insilico')
    combine('default', 'insilico', 'insilico')
    combine('validate', 'tariff', 'phmrc', extended=True)
    combine('validate', 'insilico', 'insilico', extended=True)
    # TODO: fix so that passed params are intelligible (https://xkcd.com/1695/)
    combine('default', 'insilico', 'default', extended=True)
