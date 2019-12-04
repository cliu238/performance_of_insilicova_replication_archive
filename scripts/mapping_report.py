from pathlib import Path
import re
import sys

import pandas as pd
from rpy2.robjects import globalenv
from rpy2.robjects.packages import importr, data
from rpy2.robjects.pandas2ri import ri2py


REPO = Path(__file__).resolve().parent.parent


def get_insilico_symptom_descriptions():
    insilico_r = importr('InSilicoVA')
    as_data_frame = globalenv.get('as.data.frame')
    probbase = as_data_frame(data(insilico_r).fetch('probbase')['probbase'])
    return ri2py(probbase).set_index('INDIC.C.10')['QDESC.C.70'].to_dict()


def get_phmrc_symptom_descriptions():
    key_col, val_col = 'variable', 'question'
    df = pd.read_csv(REPO / 'data/ghdx/codebook.csv')
    durations = df[val_col].str.contains('\[specify units\]')

    # Remove trailing 'a' from key
    df.loc[durations, key_col] = df.loc[durations, key_col].str.slice(0, 5)

    df.loc[durations, val_col] = df.loc[durations, val_col].str.slice(0, -15)
    descriptions = df.set_index(key_col)[val_col].to_dict()

    cats = ~durations & \
           ~df.coding.str.startswith('9').fillna(True).astype(bool) & \
           df.coding.notnull()
    coding = {col: dict(zip(map(int, re.findall('\d+(?= ")', codes)),
                            re.findall('(?<= ").+?(?=")', codes)))
              for col, codes in df.loc[cats].set_index(key_col).coding.iteritems()}

    return descriptions, coding


def main():
    sys.path.insert(0, str(REPO / 'src'))
    from map_insilico import ADULT_SYMPTOM_MAP, CHILD_SYMPTOM_MAP, \
        NEONATE_SYMPTOM_MAP

    symptom_map = {
        'adult': ADULT_SYMPTOM_MAP,
        'child': CHILD_SYMPTOM_MAP,
        'neonate': NEONATE_SYMPTOM_MAP,
    }

    insilico_symptoms = get_insilico_symptom_descriptions()
    phmrc_symptoms, coding = get_phmrc_symptom_descriptions()

    cols = ['insilico', 'insilico_description', 'phmrc', 'phmrc_description',
            'mapping']
    writer = pd.ExcelWriter(str(REPO / 'data/mapped/insilico_mapping.xlsx'))
    for module, mapping in symptom_map.items():
        out = []
        for insilico, phmrc, func in mapping:
            if not phmrc:
                continue

            if hasattr(func, 'func'):  # functools.partial objects
                func_name = func.func.__name__
                if func_name == 'between':
                    value = '{} and {}'.format(func.keywords['lower'],
                                               func.keywords['upper'])
                else:
                    value = func.keywords['val']
                    if phmrc in coding:
                        value = coding[phmrc].get(value, value)
                map_description = '{} {}'.format(func_name, value)
            else:
                map_description = 'custom'

            if isinstance(phmrc, str):
                phmrc_names = phmrc
                phmrc_description = phmrc_symptoms[phmrc]
            else:
                phmrc_names = []
                phmrc_description = []
                try:
                    for col, value in phmrc:
                        phmrc_names.append(col)
                        phmrc_description.append(phmrc_symptoms[col])
                except ValueError:
                    for col in phmrc:
                        phmrc_names.append(col)
                        phmrc_description.append(phmrc_symptoms[col])

                phmrc_names = '; '.join(phmrc_names)
                phmrc_description = ';\n'.join(phmrc_description)

            out.append([
                insilico,
                insilico_symptoms[insilico],
                phmrc_names,
                phmrc_description,
                map_description,
            ])
        pd.DataFrame(out, columns=cols).to_excel(writer, module, index=False)

    writer.save()


if __name__ == '__main__':
    main()
