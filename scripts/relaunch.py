import glob
import itertools
import os


def main():
    analyses = 'no-train'
    clf = 'insilico'
    modules = ['adult', 'child', 'neonate']
    hces = ['w_hce', 'no_hce']
    causes = 'insilico'
    symptoms = 'insilico'
    n_splits = 500
    splits = ['{i}-{i}'.format(i=i) for i in range(n_splits)]

    repo = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    subdir = '_'.join([analyses, causes, symptoms])
    globy = os.path.join(repo, 'data', subdir, '*_accuracy.csv')
    completed = [f.split(os.path.sep)[-1][:f.find('_acc')]
                 for f in glob.glob(globy)]

    params = [[analyses], [clf], modules, hces, splits, [causes], [symptoms]]
    needed = [p for p in itertools.product(*params)
              if '_'.join(p) not in completed]

    job_name = ('{analysis}_{clf}_{module}_{hce}_{causes}_{symptoms}'
                '_splits_{start}-{stop}')
    log = os.path.join(repo, 'data', 'logs', job_name)
    cmd = ('qsub -N ' + job_name + ' -P proj_va -o ' + log + ' -e ' + log +
           ' -l h="cn4*|cn50*|cn519*" '
           ' -pe multi_slot 5 -l mem_free=10g {repo}/scripts/python_w_env.sh '
           '{repo} insilico2 {repo}/src/analysis.py -a {analysis} -m {module} '
           '--clf {clf} -c {causes} -s {symptoms} {hce} --n-splits {n_splits} '
           '--subset {start} {stop} -o {outdir} ')
    for job in needed:
        keys = ['analysis', 'clf', 'module', 'hce', 'splits', 'causes',
                'symptoms']
        params = dict(zip(keys, job))
        start, stop = params.pop('splits').split('-')
        hce = params.pop('hce')
        hce = '--no-hce' if hce == 'no_hce' else ''
        params.update({
            'start': start,
            'stop': stop,
            'hce': hce,
            'repo': repo,
            'n_splits': n_splits,
            'outdir': os.path.join(repo, 'data', subdir, str(start)),
        })
        try:
             os.mkdir(params['outdir'])
        except OSError:
             pass
        #print cmd.format(**params)
        os.popen(cmd.format(**params))

if __name__ == '__main__':
    main()

