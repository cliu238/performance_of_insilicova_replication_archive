import pytest

from analysis import main


skip = pytest.mark.skip(reason='Data is not mapped')


@pytest.mark.parametrize('analysis', ['validate', 'in-sample', 'no-train'])
@pytest.mark.parametrize('module', ['adult', 'child', 'neonate'])
@pytest.mark.parametrize('symptoms', ['tariff', 'insilico'])
@pytest.mark.parametrize('hce', [True, False])
@pytest.mark.parametrize('cause_list', ['insilico', 'phmrc'])
@pytest.mark.parametrize('resample_test', [True, False])
@pytest.mark.parametrize('subset', [None, [0, 1], [1, 1]])
def test_analysis_main(tmpdir, analysis, module, symptoms, hce, cause_list,
                       resample_test, subset):
    kwargs = {
        'clf': 'random',
        'analysis': analysis,
        'module': module,
        'symptoms': symptoms,
        'hce': hce,
        'cause_list': cause_list,
        'resample_test': resample_test,
        'resample_size': 1,
        'subset': subset,
        'n_splits': 2,
        'test_size': 0.25,
        'holdout_n': 1,
        'outdir': tmpdir.strpath
    }
    main(**kwargs)
