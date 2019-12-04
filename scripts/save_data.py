import glob
import pandas as pd
import itertools
import os
import pdb

basedir = '/share/scratch/users/josephj7/repos/insilicova/data'
assert os.path.exists(basedir)
outdir = '/homes/josephj7/data/insilico'
assert os.path.exists(outdir)

modules = ['adult', 'child', 'neonate']
hces = ['w_hce', 'no_hce']
outputs = ['accuracy', 'ccc', 'csmf', 'predictions']

def combine(symptoms, causes):
    template = '{}/validate_{}_{}/validate_insilico_{}_{}_{}_{}_*_{}.csv'
    for module, hce, output in itertools.product(modules, hces, outputs):
        globby = template.format(basedir, causes, symptoms, module, hce, causes, symptoms, output)
        df = pd.concat([pd.read_csv(f) for f in glob.glob(globby)])
        outfile = '{}/results_{}_{}/validate_insilico_{}_{}_{}_{}_{}.csv'.format(
                  outdir, causes, symptoms, module, hce, causes, symptoms, output)
        df.to_csv(outfile, index=False)

def combine_default():
    template = '{}/no-train_insilico_insilico/*/default_insilico_{}_{}_{}.csv'
    for module, hce, output in itertools.product(modules, hces, outputs):
        globby = template.format(basedir, module, hce, output)
        df = pd.concat([pd.read_csv(f) for f in glob.glob(globby)])
        outfile = '{}/results_default_insilico/default_insilico_{}_{}_{}.csv'.format(
                  outdir, module, hce, output)
        df.to_csv(outfile, index=False)

if __name__ == '__main__':
    # combine('tariff', 'phmrc')
    # combine('insilico', 'insilico')
    combine_default()


