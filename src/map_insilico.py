import functools

from mapping import *


# Functions to dichotomize duration variables
# All duration variable are in days
less_than_10_mins = functools.partial(less_than, val=(10 / float(24 * 60)))
at_least_10_mins = functools.partial(at_least, val=(10 / float(24 * 60)))
less_than_1_hour = functools.partial(less_than, val=(1 / float(24)))
at_least_1_hour = functools.partial(at_least, val=(1 / float(24)))
less_than_24_hour = functools.partial(less_than, val=1)
at_least_24_hours = functools.partial(at_least, val=1)
at_least_2_days = functools.partial(at_least, val=2)
less_than_1_week = functools.partial(less_than, val=7)
at_least_1_week = functools.partial(at_least, val=7)
less_than_2_weeks = functools.partial(less_than, val=14)
at_least_2_weeks = functools.partial(at_least, val=14)
less_than_3_weeks = functools.partial(less_than, val=21)
at_least_3_weeks = functools.partial(at_least, val=21)
between_2_and_4_weeks = functools.partial(between, lower=14, upper=27)
at_least_4_weeks = functools.partial(at_least, val=28)
at_least_3_month = functools.partial(at_least, val=90)

# Child weight variables are in grams
less_than_2_half_kg = functools.partial(less_than, val=2500)
at_least_4_half_kg = functools.partial(at_least, val=4500)

# Functions to dichotomize age variables
elder = functools.partial(at_least, val=65)
midage = functools.partial(between, lower=50, upper=64)
adult = functools.partial(between, lower=15, upper=49)
child = functools.partial(between, lower=5, upper=14)
under5 = functools.partial(between, lower=1, upper=4)


def infant(row, mapping=None):
    row = row[['g5_04b', 'g5_04c']].fillna(0)
    agedays = row.g5_04b * 30 + row.g5_04c
    return int(agedays > 28 and agedays < 365)


neonate = functools.partial(less_than, val=28)
died_d1 = functools.partial(value, val=1)
died_d23 = functools.partial(between, lower=1, upper=2)
died_d36 = functools.partial(between, lower=3, upper=6)
died_w1 = functools.partial(between, lower=7, upper=28)


def magegp1(row, mapping=None):
    return int(row.g5_02 == 2 and row.g5_04a <= 19)


def magegp2(row, mapping=None):
    return int(row.g5_02 == 2 and row.g5_04a >= 20 and row.g5_04a <= 34)


def magegp3(row, mapping=None):
    return int(row.g5_02 == 2 and row.g5_04a >= 35 and row.g5_04a <= 49)


# Functions to dichotomize categoricals
def coma(row, mapping=None):
    return int(row.a2_74 == 1 and row.a2_76 > 1)


def diff_sw(row, mapping=None):
    # Difficulty with liquids or both solids and liquids
    diff_w_liquids = row.a2_59 == 2 or row.a2_59 == 3
    return int(row.a2_57 == 1 and diff_w_liquids)


def pend_6w(row, mapping=None):
    return int((row.a3_17 == 1 or row.a3_18 == 1) and row.a3_11 < 6 * 30)


# Symptom maps
# item 1 is the name of the Insilico symptom
# item 2 is a str or list of PHMRC columns, value
# item 3 is the function to use
# Symptoms are ordered correctly
ADULT_SYMPTOM_MAP = [
    # Ages
    ('elder', 'g5_04a', elder),
    ('midage', 'g5_04a', midage),
    ('adult', 'g5_04a', adult),
    ('child', 'g5_04a', child),   # catches 12- and 13-year-olds
    ('under5', None, definitely_not),
    ('infant', None, definitely_not),
    ('neonate', None, definitely_not),

    # Sex
    ('male', 'g5_02', one),
    ('female', 'g5_02', two),

    # Maternal Ages
    ('magegp1', ['g5_02', 'g5_04a'], magegp1),
    ('magegp2', ['g5_02', 'g5_04a'], magegp2),
    ('magegp3', ['g5_02', 'g5_04a'], magegp3),

    # Baby Ages (not applicable to adults)
    ('died_d1', None, definitely_not),
    ('died_d23', None, definitely_not),
    ('died_d36', None, definitely_not),
    ('died_w1', None, definitely_not),

    # Timing of the illness
    ('acute', 'a2_01', less_than_3_weeks),
    ('chronic', 'a2_01', at_least_3_weeks),
    ('sudden', 'word_sudden', one),
    ('wet_seas', None, no_data),
    ('dry_seas', None, no_data),

    # Medical history
    ('heart_dis', 'a1_01_9', one),
    ('tuber', 'a1_01_13', one),
    ('hiv_aids', 'a1_01_14', one),
    ('hypert', 'a1_01_10', one),
    ('diabetes', 'a1_01_7', one),
    ('asthma', 'a1_01_1', one),
    ('epilepsy', 'a1_01_8', one),
    ('cancer', 'a1_01_3', one),
    ('copd', 'a1_01_4', one),
    ('dement', 'a1_01_5', one),
    ('depress', 'a1_01_6', one),
    ('stroke', 'a1_01_12', one),
    ('sickle', None, no_data),
    ('kidney_dis', None, no_data),
    ('liver_dis', None, no_data),
    ('measles', None, no_data),

    # Confusion
    ('men_con', 'a2_78', one),
    ('mencon3', 'a2_79', at_least_3_month),

    # Malaria diagnosis
    ('malaria', None, no_data),
    ('malarneg', None, no_data),

    # Fever
    ('fever', 'a2_02', one),
    ('ac_fever', 'a2_03', less_than_2_weeks),
    ('ch_fever', 'a2_03', at_least_2_weeks),
    ('night_sw', 'a2_06', one),

    # Cough
    ('cough', 'a2_32', one),
    ('ac_cough', 'a2_33', less_than_3_weeks),
    ('ch_cough', 'a2_33', at_least_3_weeks),
    ('pr_cough', 'a2_34', one),
    ('bl_cough', 'a2_35', one),
    ('whoop', None, no_data),

    # Difficult breathing
    ('breath', 'a2_36', one),
    ('rapid_br', 'a2_40', one),
    ('ac_rpbr', 'a2_41', less_than_2_weeks),
    ('ch_rpbr', 'a2_41', at_least_2_weeks),
    ('br_less', None, no_data),
    ('ac_brl', 'a2_37', less_than_2_weeks),
    ('ch_brl', 'a2_37', at_least_2_weeks),
    ('exert_br', [('a2_39_1', 3), ('a2_39_2', 3)], has_any),
    ('lying_br', [('a2_39_1', 1), ('a2_39_2', 1)], has_any),
    ('chest_in', None, no_data),
    ('wheeze', 'a2_42', one),

    # Chest pain
    ('ch_pain', 'a2_43', one),

    # Yellow eyes
    ('yellow', 'a2_21', one),

    # Diarrhea
    ('diarr', 'a2_47', one),
    ('ac_diarr', 'a2_48', less_than_2_weeks),
    ('pe_diarr', 'a2_48', between_2_and_4_weeks),
    ('ch_diarr', 'a2_48', at_least_4_weeks),
    ('bl_diarr', 'a2_50', one),

    # Vomitting
    ('vomiting', 'a2_53', one),
    ('bl_vomit', 'a2_55', one),

    # Abdomin
    ('abdom', [('a2_61', 1), ('a2_64', 1), ('a2_67', 1)], has_any),
    ('abd_pain', 'a2_61', one),
    ('ac_abdp', 'a2_62', less_than_2_weeks),
    ('ch_abdp', 'a2_62', at_least_2_weeks),
    ('swe_abd', 'a2_64', one),
    ('ac_swab', 'a2_65', less_than_2_weeks),
    ('ch_swab', 'a2_65', at_least_2_weeks),
    ('abd_mass', 'a2_67', one),
    ('ac_abdm', 'a2_68', less_than_2_weeks),
    ('ch_abdm', 'a2_68', at_least_2_weeks),

    # Headaches
    ('headache', 'a2_69', one),

    # Skin
    ('skin', [('a2_07', 1), ('a2_10', 1), ('a2_12', 1)], has_any),
    ('skin_les', 'a2_10', one),
    ('sk_feet', 'a2_13', one),
    ('rash', 'a2_07', one),
    ('ac_rash', 'a2_08', less_than_1_week),
    ('ch_rash', 'a2_08', at_least_1_week),
    ('measrash', None, no_data),
    ('herpes', None, no_data),

    # Stiff neck
    ('stiff_neck', 'a2_72', one),
    ('ac_stnk', 'a2_73', less_than_1_week),
    ('ch_stnk', 'a2_73', at_least_1_week),

    # Unconscious
    ('coma', ['a2_74', 'a2_76'], coma),
    ('co_ons', 'a2_75', one),

    # Convulsions
    ('convul', 'a2_82', one),
    ('ac_conv', 'a2_83', less_than_10_mins),
    ('ch_conv', 'a2_83', at_least_10_mins),
    ('unc_con', 'a2_84', one),

    # Urine
    ('urine', None, no_data),
    ('uri_ret', 'a2_52', one),
    ('exc_urine', None, no_data),
    ('uri_haem', None, no_data),

    # Weight loss
    ('wt_loss', 'a2_18', one),
    ('wasting', None, no_data),

    # Thrush
    ('or_cand', None, no_data),

    # Rigidity
    ('rigidity', None, no_data),

    # Swelling and lumps
    ('swell', [
        ('a2_29', 1),
        ('a2_30', 1),
        ('a3_01', 1),
        ('a2_31', 1)
    ], has_any),
    ('swe_oral', None, no_data),
    ('swe_neck', 'a2_29', one),
    ('swe_armp', 'a2_30', one),
    ('swe_breast', [('a3_01', 1), ('a3_02', 1)], has_any),
    ('swe_gen', 'a2_31', one),
    ('swe_oth', 'a2_25', one),
    ('swe_legs', 'a2_23', one),

    # Malenutrition
    ('anaemia', 'a2_20', one),
    ('exc_drink', None, no_data),
    ('hair', None, no_data),

    # Paralysis on one side
    ('paral_one', [('a2_87_1', 1), ('a2_87_2', 1)], has_any),

    # Sunken eone
    ('eye_sunk', None, no_data),

    # Bleed from orificies
    ('bl_orif', None, no_data),

    # Intermenstrual bleeding
    ('vb_bet', 'a3_05', one),
    ('vb_men', 'a3_03', one),
    ('vb_after', 'a3_04', one),

    # Swallowing
    ('diff_sw', ['a2_57', 'a2_59'], diff_sw),

    # Maternal
    ('not_preg', 'a3_10', zero),
    ('pregnant', 'a3_10', one),
    ('del_6wks', 'a3_18', one),
    ('pend_6w', ['a3_17', 'a3_18', 'a3_11'], pend_6w),
    ('first_p', None, no_data),
    ('more4', None, no_data),
    ('cs_prev', None, no_data),
    ('multip', None, no_data),

    # labor
    ('lab_24', 'a3_16', at_least_24_hours),
    ('died_lab', 'a3_15', one),
    ('death_24', None, no_data),

    ('baby_al', 'a3_18', one),
    ('breast_fd', None, no_data),

    # Delivery location
    ('del_fac', None, no_data),
    ('del_home', None, no_data),
    ('del_else', None, no_data),

    # Delivery type
    ('prof_ass', None, no_data),
    ('del_norm', None, no_data),
    ('del_ass', None, no_data),
    ('del_cs', None, no_data),
    ('del_home', None, no_data),

    ('baby_pos', None, no_data),
    ('mon_early', None, no_data),
    ('hyster', None, no_data),

    # Hypertensive
    ('bpr_preg', None, no_data),
    ('fit_preg', [('a3_10', 1), ('a2_82', 1)], has_all),
    ('vis_bl', None, no_data),

    # Hemorrhage
    ('bleed', 'a3_06', one),
    ('e_bleed', None, no_data),
    ('s_bleed', None, no_data),
    ('d_bleed', 'a3_14', one),
    ('p_bleed', 'a3_19', one),

    # Sepsis
    ('placent_r', None, no_data),
    ('disch_sm', 'a3_20', one),

    # Abortion
    ('term_att', 'a3_12', one),
    ('abort', 'a3_17', one),

    # Duration
    ('born_early', None, no_data),
    ('born_3437', None, no_data),
    ('born_38', None, no_data),

    # Child questions
    ('ab_size', None, no_data),
    ('born_small', None, no_data),
    ('born_big', None, no_data),
    ('twin', None, no_data),
    ('comdel', None, no_data),
    ('cord', None, no_data),
    ('waters', None, no_data),
    ('move_lb', None, no_data),
    ('cyanosis', None, no_data),
    ('baby_br', None, no_data),
    ('born_nobr', None, no_data),
    ('cried', None, no_data),
    ('no_life', None, no_data),
    ('mushy', None, no_data),
    ('fed_d1', None, no_data),
    ('st_suck', None, no_data),
    ('ab_posit', None, no_data),
    ('conv_d1', None, no_data),
    ('conv_d2', None, no_data),
    ('arch_b', None, no_data),
    ('font_hi', None, no_data),
    ('font_lo', None, no_data),
    ('unw_d1', None, no_data),
    ('unw_d2', None, no_data),
    ('cold', None, no_data),
    ('umbinf', None, no_data),
    ('b_yellow', None, no_data),
    ('devel', None, no_data),
    ('born_malf', None, no_data),
    ('mlf_bk', None, no_data),
    ('mlf_lh', None, no_data),
    ('mlf_sh', None, no_data),
    ('mttv', None, no_data),
    ('b_norm', None, no_data),
    ('b_assist', None, no_data),
    ('b_caes', None, no_data),
    ('b_first', None, no_data),
    ('b_more4', None, no_data),
    ('b_mbpr', None, no_data),
    ('b_msmds', None, no_data),
    ('b_mcon', None, no_data),
    ('b_mbvi', None, no_data),
    ('b_mvbl', None, no_data),
    ('b_bfac', None, no_data),
    ('b_bhome', None, no_data),
    ('b_bway', None, no_data),
    ('b_bprof', None, no_data),

    # Injuries
    ('injury', [
        ('a5_01_1', 1),
        ('a5_01_2', 1),
        ('a5_01_3', 1),
        ('a5_01_6', 1),
        ('a5_01_7', 1),
        ('a5_01_5', 1),
        ('a5_01_4', 1),
        ('a5_03', 1),
        ('a5_02', 1),
    ], has_any),
    ('traffic', 'a5_01_1', one),
    ('o_trans', None, no_data),
    ('fall', 'a5_01_2', one),
    ('drown', 'a5_01_3', one),
    ('fire', 'a5_01_6', one),
    ('assault', 'a5_01_7', one),
    ('venom', 'a5_01_5', one),
    ('force', None, no_data),
    ('poison', 'a5_01_4', one),
    ('inflict', 'a5_03', one),
    ('suicide', 'a5_02', one),

    # Risk factors
    ('alcohol', 'a4_05', one),
    ('smoking', 'a4_01', one),
    ('married', 'g1_08', two),

    # Health Care
    ('vaccin', None, no_data),
    ('treat', None, no_data),
    ('t_ort', None, no_data),
    ('t_iv', None, no_data),
    ('blood_tr', None, no_data),
    ('t_ngt', None, no_data),
    ('antib_i', None, no_data),
    ('surgery', None, no_data),
    ('sur_1m', None, no_data),
    ('disch', None, no_data),
    ('shospf', [
        ('a6_02_4', 1),
        ('a6_02_5', 1),
        ('a6_02_6', 1),
        ('a6_02_7', 1),
    ], has_any),
    ('strans', None, no_data),
    ('sadmit', None, no_data),
    ('streat', None, no_data),
    ('smedic', None, no_data),
    ('smore2', None, no_data),
    ('sdoubt', None, no_data),
    ('stradm', 'a6_02_1', one),
    ('smobph', None, no_data),
    ('scosts', None, no_data),
]

CHILD_SYMPTOM_MAP = [
    # Ages
    ('elder', None, definitely_not),
    ('midage', None, definitely_not),
    ('adult', None, definitely_not),
    ('child', 'g5_04a', child),
    ('under5', 'g5_04a', under5),
    ('infant', ['g5_04b', 'g5_04c'], infant),
    ('neonate', None, definitely_not),

    # Sex
    ('male', 'g5_02', one),
    ('female', 'g5_02', two),

    # Maternal Ages
    ('magegp1', None, definitely_not),
    ('magegp2', None, definitely_not),
    ('magegp3', None, definitely_not),

    # Baby Ages
    ('died_d1', None, definitely_not),
    ('died_d23', None, definitely_not),
    ('died_d36', None, definitely_not),
    ('died_w1', None, definitely_not),

    # Timing of the illness
    ('acute', 'c1_21', less_than_3_weeks),
    ('chronic', 'c1_21', at_least_3_weeks),
    ('sudden', 'word_sudden', one),
    ('wet_seas', None, no_data),
    ('dry_seas', None, no_data),

    # Medical history
    ('heart_dis', None, no_data),
    ('tuber', None, no_data),
    ('hiv_aids', 'c5_18', one),
    ('hypert', None, no_data),
    ('diabetes', None, no_data),
    ('asthma', None, no_data),
    ('epilepsy', None, no_data),
    ('cancer', None, no_data),
    ('copd', None, no_data),
    ('dement', None, no_data),
    ('depress', None, no_data),
    ('stroke', None, no_data),
    ('sickle', None, no_data),
    ('kidney_dis', None, no_data),
    ('liver_dis', None, no_data),
    ('measles', None, no_data),

    # Confusion
    ('men_con', None, no_data),
    ('mencon3', None, no_data),

    # Malaria diagnosis
    ('malaria', None, no_data),
    ('malarneg', None, no_data),

    # Fever
    ('fever', 'c4_01', one),
    ('ac_fever', 'c4_02', less_than_2_weeks),
    ('ch_fever', 'c4_02', at_least_2_weeks),
    ('night_sw', 'c4_05', three),   # pattern: only at night

    # Cough
    ('cough', 'c4_12', one),
    ('ac_cough', 'c4_13', less_than_3_weeks),
    ('ch_cough', 'c4_13', at_least_3_weeks),
    ('pr_cough', None, no_data),
    ('bl_cough', None, no_data),
    ('whoop', None, no_data),

    # Difficult breathing
    ('breath', 'c4_16', one),
    ('rapid_br', 'c4_18', one),
    ('ac_rpbr', 'c4_19', less_than_2_weeks),
    ('ch_rpbr', 'c4_19', at_least_2_weeks),
    ('br_less', None, no_data),
    ('ac_brl', None, no_data),
    ('ch_brl', None, no_data),
    ('exert_br', None, no_data),
    ('lying_br', None, no_data),
    ('chest_in', 'c4_20', one),
    ('wheeze', 'c4_24', one),

    # Chest pain
    ('ch_pain', None, no_data),

    # Yellow eone
    ('yellow', None, no_data),

    # Diarrhea
    ('diarr', 'c4_06', one),
    ('ac_diarr', 'c4_08', less_than_2_weeks),
    ('pe_diarr', 'c4_08', between_2_and_4_weeks),
    ('ch_diarr', 'c4_08', at_least_4_weeks),
    ('bl_diarr', 'c4_11', one),

    # Vomitting
    ('vomiting', None, no_data),
    ('bl_vomit', None, no_data),

    # Abdomin
    ('abdom', None, no_data),
    ('abd_pain', None, no_data),
    ('ac_abdp', None, no_data),
    ('ch_abdp', None, no_data),
    ('swe_abd', 'c4_40', one),
    ('ac_swab', None, no_data),
    ('ch_swab', None, no_data),
    ('abd_mass', None, no_data),
    ('ac_abdm', None, no_data),
    ('ch_abdm', None, no_data),

    # Headaches
    ('headache', None, no_data),

    # Skin
    ('skin', [('c4_30', 1), ('c4_38', 1), ('c4_46', 1)], has_any),
    ('skin_les', None, no_data),
    ('sk_feet', None, no_data),
    ('rash', 'c4_30', one),
    ('ac_rash', 'c4_33', less_than_1_week),
    ('ch_rash', 'c4_33', at_least_1_week),
    ('measrash', 'c4_43', one),
    ('herpes', None, no_data),

    # Stiff neck
    ('stiff_neck', 'c4_28', one),
    ('ac_stnk', None, no_data),
    ('ch_stnk', None, no_data),

    # Unconscious
    ('coma', 'c4_26', one),
    ('co_ons', 'c4_27', less_than_24_hour),

    # Convulsions
    ('convul', 'c4_25', one),
    ('ac_conv', None, no_data),
    ('ch_conv', None, no_data),
    ('unc_con', None, no_data),

    # Urine
    ('urine', None, no_data),
    ('uri_ret', None, no_data),
    ('exc_urine', None, no_data),
    ('uri_haem', None, no_data),

    # Weight loss
    ('wt_loss', None, no_data),
    ('wasting', 'c4_35', one),

    # Thrush
    ('or_cand', None, no_data),

    # Rigidity
    ('rigidity', None, no_data),   # whole body paralysis

    # Swelling and lumps
    ('swell', [('c4_42', 1), ('c4_36', 1)], has_any),
    ('swe_oral', None, no_data),
    ('swe_neck', None, no_data),
    ('swe_armp', 'c4_42', one),
    ('swe_breast', None, no_data),
    ('swe_gen', None, no_data),
    ('swe_oth', None, no_data),
    ('swe_legs', 'c4_36', one),

    # Malenutrition
    ('anaemia', 'c4_41', one),
    ('exc_drink', None, no_data),
    ('hair', 'c4_39', one),

    # Paralysis on one side
    ('paral_one', None, no_data),

    # Sunken eone
    ('eye_sunk', None, no_data),

    # Bleed from orificies
    ('bl_orif', 'c4_44', one),

    # Intermenstrual bleeding
    ('vb_bet', None, definitely_not),
    ('vb_men', None, definitely_not),
    ('vb_after', None, definitely_not),

    # Swallowing
    ('diff_sw', None, definitely_not),

    # Maternal
    ('not_preg', None, definitely_not),
    ('pregnant', None, definitely_not),
    ('del_6wks', None, definitely_not),
    ('pend_6w', None, definitely_not),
    ('first_p', None, definitely_not),
    ('more4', None, definitely_not),
    ('cs_prev', None, definitely_not),
    ('multip', None, definitely_not),

    # labor
    ('lab_24', None, definitely_not),
    ('died_lab', None, definitely_not),
    ('death_24', None, definitely_not),

    ('baby_al', None, definitely_not),
    ('breast_fd', None, definitely_not),

    # Delivery location
    ('del_fac', None, definitely_not),
    ('del_home', None, definitely_not),
    ('del_else', None, definitely_not),

    # Delivery type
    ('prof_ass', None, definitely_not),
    ('del_norm', None, definitely_not),
    ('del_ass', None, definitely_not),
    ('del_cs', None, definitely_not),
    ('del_home', None, definitely_not),

    ('baby_pos', None, definitely_not),
    ('mon_early', None, definitely_not),
    ('hyster', None, definitely_not),

    # Hypertensive
    ('bpr_preg', None, definitely_not),
    ('fit_preg', None, definitely_not),
    ('vis_bl', None, definitely_not),

    # Hemorrhage
    ('bleed', None, definitely_not),
    ('e_bleed', None, definitely_not),
    ('s_bleed', None, definitely_not),
    ('d_bleed', None, definitely_not),
    ('p_bleed', None, definitely_not),

    # Sepsis
    ('placent_r', None, definitely_not),
    ('disch_sm', None, definitely_not),

    # Abortion
    ('term_att', None, definitely_not),
    ('abort', None, definitely_not),

    # Duration
    ('born_early', None, definitely_not),
    ('born_3437', None, definitely_not),
    ('born_38', None, definitely_not),

    # Child questions
    ('ab_size', None, no_data),
    ('born_small', 'c1_08b', less_than_2_half_kg),
    ('born_big', 'c1_08b', at_least_4_half_kg),
    ('twin', 'c1_01', two),

    # Pregnancy complications
    ('comdel', None, no_data),
    ('cord', None, no_data),
    ('waters', None, no_data),
    ('move_lb', None, no_data),
    ('cyanosis', None, no_data),

    # Stillbirth
    ('baby_br', 'c1_14', one),
    ('born_nobr', None, no_data),
    ('cried', 'c1_12', one),
    ('no_life', 'c1_15', one),
    ('mushy', None, no_data),

    # Suckling
    ('fed_d1', None, no_data),
    ('st_suck', None, no_data),

    # Delivery position
    ('ab_posit', None, no_data),

    # Tetanus
    ('conv_d1', None, no_data),
    ('conv_d2', None, no_data),
    ('arch_b', None, no_data),

    # Fontanelle
    ('font_hi', 'c4_29', one),
    ('font_lo', None, no_data),

    # Unresponsive duration
    ('unw_d1', None, no_data),
    ('unw_d2', None, no_data),

    # Cold to touch
    ('cold', None, no_data),

    # Umibilical discharge
    ('umbinf', None, no_data),

    # Yellow extremities
    ('b_yellow', None, no_data),

    # Slow development
    ('devel', None, no_data),

    # Birth defects
    ('born_malf', 'c1_18', one),
    ('mlf_bk', 'c1_19_3', one),
    ('mlf_lh', 'c1_19_2', one),
    ('mlf_sh', 'c1_19_1', one),

    # Tetanus vaccine
    ('mttv', None, no_data),

    # Delivery type
    ('b_norm', None, no_data),
    ('b_assist', None, no_data),
    ('b_caes', None, no_data),

    # Birth order
    ('b_first', None, no_data),
    ('b_more4', None, no_data),

    # Maternal complications
    ('b_mbpr', None, no_data),
    ('b_msmds', None, no_data),
    ('b_mcon', None, no_data),
    ('b_mbvi', None, no_data),
    ('b_mvbl', None, no_data),

    # Place of birth
    ('b_bfac', [('c1_06a', 1), ('c1_06a', 2)], has_any),
    ('b_bhome', 'c1_06a', four),
    ('b_bway', [('c1_06a', 3), ('c1_06a', 5)], has_any),
    ('b_bprof', None, no_data),

    # Injuries
    ('injury', [
        ('c4_47_1', 1),
        ('c4_47_2', 1),
        ('c4_47_3', 1),
        ('c4_47_6', 1),
        ('c4_47_7', 1),
        ('c4_47_5', 1),
        ('c4_47_4', 1),
        ('c4_48', 1),
    ], has_any),
    ('traffic', 'c4_47_1', one),
    ('o_trans', None, no_data),
    ('fall', 'c4_47_2', one),
    ('drown', 'c4_47_3', one),
    ('fire', 'c4_47_6', one),
    ('assault', 'c4_47_7', one),
    ('venom', 'c4_47_5', one),
    ('force', None, no_data),
    ('poison', 'c4_47_4', one),
    ('inflict', 'c4_48', one),
    ('suicide', None, no_data),

    # Risk factors
    ('alcohol', None, no_data),
    ('smoking', None, no_data),
    ('married', None, no_data),

    # Health Care
    ('vaccin', None, no_data),
    ('treat', None, no_data),
    ('t_ort', None, no_data),
    ('t_iv', None, no_data),
    ('blood_tr', None, no_data),
    ('t_ngt', None, no_data),
    ('antib_i', None, no_data),
    ('surgery', None, no_data),
    ('sur_1m', None, no_data),
    ('disch', None, no_data),
    ('shospf', [
        ('c5_02_4', 1),
        ('c5_02_5', 1),
        ('c5_02_6', 1),
    ], has_any),
    ('strans', None, no_data),
    ('sadmit', None, no_data),
    ('streat', None, no_data),
    ('smedic', None, no_data),
    ('smore2', None, no_data),
    ('sdoubt', None, no_data),
    ('stradm', 'c5_02_1', one),
    ('smobph', None, no_data),
    ('scosts', None, no_data),
]

NEONATE_SYMPTOM_MAP = [
    # Ages
    ('elder', None, definitely_not),
    ('midage', None, definitely_not),
    ('adult', None, definitely_not),
    ('child', None, definitely_not),
    ('under5', None, definitely_not),
    ('infant', None, definitely_not),
    ('neonate', 'g5_04c', neonate),

    # Sex
    ('male', 'g5_02', one),
    ('female', 'g5_02', two),

    # Maternal Ages
    ('magegp1', None, definitely_not),
    ('magegp2', None, definitely_not),
    ('magegp3', None, definitely_not),

    # Baby Ages
    ('died_d1', None, died_d1),
    ('died_d23', None, died_d23),
    ('died_d36', None, died_d36),
    ('died_w1', None, died_w1),

    # Timing of the illness
    ('acute', 'c1_21', less_than_3_weeks),
    ('chronic', 'c1_21', at_least_3_weeks),
    ('sudden', 'word_sudden', one),
    ('wet_seas', None, no_data),
    ('dry_seas', None, no_data),

    # Medical history
    ('heart_dis', None, no_data),
    ('tuber', None, no_data),
    ('hiv_aids', 'c5_18', one),
    ('hypert', None, no_data),
    ('diabetes', None, no_data),
    ('asthma', None, no_data),
    ('epilepsy', None, no_data),
    ('cancer', None, no_data),
    ('copd', None, no_data),
    ('dement', None, no_data),
    ('depress', None, no_data),
    ('stroke', None, no_data),
    ('sickle', None, no_data),
    ('kidney_dis', None, no_data),
    ('liver_dis', None, no_data),
    ('measles', None, no_data),

    # Confusion
    ('men_con', None, no_data),
    ('mencon3', None, no_data),

    # Malaria diagnosis
    ('malaria', None, no_data),
    ('malarneg', None, no_data),

    # Fever
    ('fever', 'c3_26', one),
    ('ac_fever', 'c3_28', less_than_2_weeks),
    ('ch_fever', 'c3_28', at_least_2_weeks),
    ('night_sw', None, no_data),

    # Cough
    ('cough', None, no_data),
    ('ac_cough', None, no_data),
    ('ch_cough', None, no_data),
    ('pr_cough', None, no_data),
    ('bl_cough', None, no_data),
    ('whoop', None, no_data),

    # Difficult breathing
    ('breath', [('c3_05', 1), ('c3_17', 1), ('c3_20', 1)], has_any),
    ('rapid_br', 'c3_20', one),
    ('ac_rpbr', 'c3_22', less_than_2_weeks),
    ('ch_rpbr', 'c3_22', at_least_2_weeks),
    ('br_less', 'c3_17', one),
    ('ac_brl', 'c3_19', less_than_2_weeks),
    ('ch_brl', 'c3_19', at_least_2_weeks),
    ('exert_br', None, no_data),
    ('lying_br', None, no_data),
    ('chest_in', 'c3_23', one),
    ('wheeze', None, no_data),

    # Chest pain
    ('ch_pain', None, no_data),

    # Yellow eyes
    ('yellow', 'c3_48', one),

    # Diarrhea
    ('diarr', 'c3_44', one),
    ('ac_diarr', None, no_data),
    ('pe_diarr', None, no_data),
    ('ch_diarr', None, no_data),
    ('bl_diarr', None, no_data),

    # Vomitting
    ('vomiting', 'c3_46', one),
    ('bl_vomit', None, no_data),

    # Abdomin
    ('abdom', None, no_data),
    ('abd_pain', None, no_data),
    ('ac_abdp', None, no_data),
    ('ch_abdp', None, no_data),
    ('swe_abd', None, no_data),
    ('ac_swab', None, no_data),
    ('ch_swab', None, no_data),
    ('abd_mass', None, no_data),
    ('ac_abdm', None, no_data),
    ('ch_abdm', None, no_data),

    # Headaches
    ('headache', None, no_data),

    # Skin
    ('skin', [
        ('c3_38', 1),
        ('c3_39', 1),
        ('c3_40', 1),
        ('c3_41', 1)
    ], has_any),
    ('skin_les', 'c3_39', one),
    ('sk_feet', None, no_data),
    ('rash', 'c3_40', one),
    ('ac_rash', None, no_data),
    ('ch_rash', None, no_data),
    ('measrash', None, no_data),
    ('herpes', None, no_data),

    # Stiff neck
    ('stiff_neck', None, no_data),
    ('ac_stnk', None, no_data),
    ('ch_stnk', None, no_data),

    # Unconscious
    ('coma', None, no_data),
    ('co_ons', None, no_data),

    # Convulsions
    ('convul', 'c3_25', one),
    ('ac_conv', None, no_data),
    ('ch_conv', None, no_data),
    ('unc_con', None, no_data),

    # Urine
    ('urine', None, no_data),
    ('uri_ret', None, no_data),
    ('exc_urine', None, no_data),
    ('uri_haem', None, no_data),

    # Weight loss
    ('wt_loss', None, no_data),
    ('wasting', None, no_data),

    # Thrush
    ('or_cand', None, no_data),

    # Rigidity
    ('rigidity', None, no_data),   # whole body paralysis

    # Swelling and lumps
    ('swell', None, no_data),
    ('swe_oral', None, no_data),
    ('swe_neck', None, no_data),
    ('swe_armp', None, no_data),
    ('swe_breast', None, no_data),
    ('swe_gen', None, no_data),
    ('swe_oth', None, no_data),
    ('swe_legs', None, no_data),

    # Malenutrition
    ('anaemia', None, no_data),
    ('exc_drink', None, no_data),
    ('hair', None, no_data),

    # Paralysis on one side
    ('paral_one', None, no_data),

    # Sunken eyes
    ('eye_sunk', None, no_data),

    # Bleed from orificies
    ('bl_orif', 'c3_42', one),

    # Intermenstrual bleeding
    ('vb_bet', None, no_data),
    ('vb_men', None, no_data),
    ('vb_after', None, no_data),

    # Swallowing
    ('diff_sw', None, no_data),

    # Maternal
    ('not_preg', None, definitely_not),
    ('pregnant', None, definitely_not),
    ('del_6wks', None, definitely_not),
    ('pend_6w', None, definitely_not),
    ('first_p', None, definitely_not),
    ('more4', None, definitely_not),
    ('cs_prev', None, definitely_not),
    ('multip', None, definitely_not),

    # labor
    ('lab_24', None, definitely_not),
    ('died_lab', None, definitely_not),
    ('death_24', None, definitely_not),

    ('baby_al', None, definitely_not),
    ('breast_fd', None, definitely_not),

    # Delivery location
    ('del_fac', None, definitely_not),
    ('del_home', None, definitely_not),
    ('del_else', None, definitely_not),

    # Delivery type
    ('prof_ass', None, definitely_not),
    ('del_norm', None, definitely_not),
    ('del_ass', None, definitely_not),
    ('del_cs', None, definitely_not),
    ('del_home', None, definitely_not),

    ('baby_pos', None, definitely_not),
    ('mon_early', None, definitely_not),
    ('hyster', None, definitely_not),

    # Hypertensive
    ('bpr_preg', None, definitely_not),
    ('fit_preg', None, definitely_not),
    ('vis_bl', None, definitely_not),

    # Hemorrhage
    ('bleed', None, definitely_not),
    ('e_bleed', None, definitely_not),
    ('s_bleed', None, definitely_not),
    ('d_bleed', None, definitely_not),
    ('p_bleed', None, definitely_not),

    # Sepsis
    ('placent_r', None, definitely_not),
    ('disch_sm', None, definitely_not),

    # Abortion
    ('term_att', None, definitely_not),
    ('abort', None, definitely_not),

    # Duration
    ('born_early', None, definitely_not),
    ('born_3437', None, definitely_not),
    ('born_38', None, definitely_not),

    # Child questions
    ('ab_size', None, no_data),
    ('born_small', 'c1_08b', less_than_2_half_kg),
    ('born_big', 'c1_08b', at_least_4_half_kg),
    ('twin', 'c1_01', two),

    # Pregnancy complications
    ('comdel', [
        ('c2_01_1', 1),
        ('c2_01_2', 1),
        ('c2_01_3', 1),
        ('c2_01_4', 1),
        ('c2_01_5', 1),
        ('c2_01_6', 1),
        ('c2_01_7', 1),
        ('c2_01_8', 1),
        ('c2_01_9', 1),
        ('c2_01_14', 1),
    ], has_any),
    ('cord', 'c2_01_7', one),
    ('waters', 'c2_07', two),
    ('move_lb', 'c2_04', zero),
    ('cyanosis', None, no_data),

    # Stillbirth
    ('baby_br', 'c1_14', one),
    ('born_nobr', 'c3_06', one),
    ('cried', 'c1_12', one),
    ('no_life', 'c1_15', one),
    ('mushy', None, no_data),

    # Suckling
    ('fed_d1', 'c3_11', one),
    ('st_suck', 'c3_14', at_least_2_days),

    # Delivery position
    ('ab_posit', 'c2_01_5', one),

    # Tetanus
    ('conv_d1', 'c3_25', one),
    ('conv_d2', 'c3_25', one),
    ('arch_b', None, no_data),

    # Fontanelle
    ('font_hi', 'c3_34', one),
    ('font_lo', None, no_data),

    # Unresponsive duration
    ('unw_d1', 'c3_33', one),
    ('unw_d2', 'c3_33', one),

    # Cold to touch
    ('cold', 'c3_29', one),

    # Umibilical discharge
    ('umbinf', 'c3_35', one),

    # Yellow extremities
    ('b_yellow', 'c3_47', one),

    # Slow development
    ('devel', None, no_data),

    # Birth defects
    ('born_malf', [('c1_18', 1), ('c3_02', 1)], has_any),
    ('mlf_bk', [('c1_19_3', 1), ('c3_03_3', 1)], has_any),
    ('mlf_lh', [('c1_19_2', 1), ('c3_03_2', 1)], has_any),
    ('mlf_sh', [('c1_19_1', 1), ('c3_03_1', 1)], has_any),

    # Tetanus vaccine
    ('mttv', None, no_data),

    # Delivery type
    ('b_norm', 'c2_17', two),
    ('b_assist', 'c2_17', one),
    ('b_caes', 'c2_17', four),

    # Birth order
    ('b_first', None, no_data),
    ('b_more4', None, no_data),

    # Maternal complications
    ('b_mbpr', 'c2_01_2', one),
    ('b_msmds', None, no_data),
    ('b_mcon', 'c2_01_1', one),
    ('b_mbvi', None, no_data),
    ('b_mvbl', None, no_data),

    # Place of birth
    ('b_bfac', [('c1_06a', 1), ('c1_06a', 2)], has_any),
    ('b_bhome', 'c1_06a', four),
    ('b_bway', [('c1_06a', 3), ('c1_06a', 5)], has_any),
    ('b_bprof', None, no_data),

    # Injuries
    ('injury', None, no_data),
    ('traffic', None, no_data),
    ('o_trans', None, no_data),
    ('fall', None, no_data),
    ('drown', None, no_data),
    ('fire', None, no_data),
    ('assault', None, no_data),
    ('venom', None, no_data),
    ('force', None, no_data),
    ('poison', None, no_data),
    ('inflict', None, no_data),
    ('suicide', None, no_data),

    # Risk factors
    ('alcohol', None, no_data),
    ('smoking', None, no_data),
    ('married', None, no_data),

    # Health Care
    ('vaccin', None, no_data),
    ('treat', None, no_data),
    ('t_ort', None, no_data),
    ('t_iv', None, no_data),
    ('blood_tr', None, no_data),
    ('t_ngt', None, no_data),
    ('antib_i', None, no_data),
    ('surgery', None, no_data),
    ('sur_1m', None, no_data),
    ('disch', None, no_data),
    ('shospf', [
        ('c5_02_4', 1),
        ('c5_02_5', 1),
        ('c5_02_6', 1),
    ], has_any),
    ('strans', None, no_data),
    ('sadmit', None, no_data),
    ('streat', None, no_data),
    ('smedic', None, no_data),
    ('smore2', None, no_data),
    ('sdoubt', None, no_data),
    ('stradm', 'c5_02_1', one),
    ('smobph', None, no_data),
    ('scosts', None, no_data),
]

ADULT_PHMRC_TO_INSILICO_CAUSE_MAP = {
    'Cirrhosis': 'Liver cirrhosis',
    'Epilepsy': 'Epilepsy',
    'Pneumonia': 'Acute resp infect incl pneumonia',
    'COPD': 'Chronic obstructive pulmonary dis',
    'Acute Myocardial Infarction': 'Acute cardiac disease',
    'Fires': 'Accid expos to smoke fire & flame',
    'Renal Failure': 'Renal failure',
    'AIDS with TB': 'HIV/AIDS related death',
    'Lung Cancer': 'Respiratory neoplasms',
    'Sepsis': 'Pregnancy-related sepsis',
    'Anemia': 'Anaemia of pregnancy',
    'Drowning': 'Accid drowning and submersion',
    'Inflammatory Heart Disease': 'Acute cardiac disease',
    'AIDS': 'HIV/AIDS related death',
    'Other Digestive Diseases': 'Acute abdomen',
    'Falls': 'Accid fall',
    'Stroke': 'Stroke',
    'Road Traffic': 'Road traffic accident',
    'Bite of Venomous Animal': 'Contact with venomous plant/animal',
    'Diabetes with Coma': 'Diabetes mellitus',
    'Congestive Heart Failure': 'Other and unspecified cardiac dis',
    'Other Infectious Diseases': 'Other and unspecified infect dis',
    'TB': 'Pulmonary tuberculosis',
    'Diabetes with Renal Failure': 'Diabetes mellitus',
    'Hypertensive Disorder': 'Pregnancy-induced hypertension',
    'Suicide': 'Intentional self-harm',
    'Other Injuries': 'Other and unspecified external CoD',
    'Hemorrhage': 'Obstetric haemorrhage',
    'Cervical Cancer': 'Reproductive neoplasms MF',
    'Malaria': 'Malaria',
    'Asthma': 'Asthma',
    'Diarrhea/Dysentery': 'Diarrhoeal diseases',
    'Colorectal Cancer': 'Other and unspecified neoplasms',
    'Homicide': 'Assault',
    'Other Cardiovascular Diseases': 'Other and unspecified cardiac dis',
    'Breast Cancer': 'Breast neoplasms',
    'Diabetes with Skin Infection/Sepsis': 'Diabetes mellitus',
    'Other Cancers': 'Other and unspecified neoplasms',
    'Lymphomas': 'Other and unspecified neoplasms',
    'Leukemia': 'Other and unspecified neoplasms',
    'Poisonings': 'Accid poisoning & noxious subs',
    'Other Non-communicable Diseases': 'Other and unspecified NCD',
    'Other Pregnancy-Related Deaths': 'Other and unspecified maternal CoD',
    'Prostate Cancer': 'Reproductive neoplasms MF',
    'Esophageal Cancer': 'Digestive neoplasms',
    'Stomach Cancer': 'Digestive neoplasms'
}

CHILD_PHMRC_TO_INSILICO_CAUSE_MAP = {
    'AIDS': 'HIV/AIDS related death',
    'Bite of Venomous Animal': 'Contact with venomous plant/animal',
    'Diarrhea/Dysentery': 'Diarrhoeal diseases',
    'Drowning': 'Accid drowning and submersion',
    'Encephalitis': 'Meningitis and encephalitis',
    'Falls': 'Accid fall',
    'Fires': 'Accid expos to smoke fire & flame',
    'Hemorrhagic fever': 'Haemorrhagic fever',
    'Malaria': 'Malaria',
    'Measles': 'Measles',
    'Meningitis': 'Meningitis and encephalitis',
    'Other Cancers': 'Other and unspecified neoplasms',
    'Other Cardiovascular Diseases': 'Other and unspecified cardiac dis',
    'Other Defined Causes of Child Deaths': 'Other and unspecified NCD',
    'Other Digestive Diseases': 'Acute abdomen',
    'Other Infectious Diseases': 'Other and unspecified infect dis',
    'Pneumonia': 'Acute resp infect incl pneumonia',
    'Poisonings': 'Accid poisoning & noxious subs',
    'Road Traffic': 'Road traffic accident',
    'Sepsis': 'Sepsis (non-obstetric)',
    'Violent Death': 'Assault',
}

NEONATE_PHMRC_TO_INSILICO_CAUSE_MAP = {
    'Birth asphyxia': 'Birth asphyxia',
    'Congenital malformation': 'Congenital malformation',
    'Meningitis/Sepsis': 'Meningitis and encephalitis',
    'Sepsis with Local Bacterial Infection': 'Neonatal sepsis',
    'Pneumonia': 'Neonatal pneumonia',
    'Preterm Delivery without Respiratory Distress Syndrome': 'Prematurity',
    'Preterm Delivery (without RDS) and Birth Asphyxia': 'Prematurity',
    'Preterm Delivery (with or without RDS) and Sepsis': 'Prematurity',
    'Preterm Delivery (without RDS) and Sepsis and Birth Asphyxia': 'Prematurity',
    'Preterm Delivery with Respiratory Distress Syndrome': 'Prematurity',
    'Stillbirth': 'Fresh stillbirth',
}

INSILICO_SYMPTOM_MAP = {
    'adult': ADULT_SYMPTOM_MAP,
    'child': CHILD_SYMPTOM_MAP,
    'neonate': NEONATE_SYMPTOM_MAP
}

INSILICO_CAUSE_MAP = {
    'adult': ADULT_PHMRC_TO_INSILICO_CAUSE_MAP,
    'child': CHILD_PHMRC_TO_INSILICO_CAUSE_MAP,
    'neonate': NEONATE_PHMRC_TO_INSILICO_CAUSE_MAP
}

INSILICO_HCE_COLUMNS = {
    'adult': [
        'sudden',
        'heart_dis',
        'tuber',
        'hiv_aids',
        'hypert',
        'diabetes',
        'asthma',
        'epilepsy',
        'cancer',
        'copd',
        'dement',
        'depress',
        'stroke',
    ],
    'child': [
        'born_small',
        'born_big',
        'sudden',
    ],
    'neonate': [
        'born_small',
        'born_big',
        'sudden',
    ],
}


if __name__ == '__main__':
    map_all_modules('insilico', INSILICO_SYMPTOM_MAP, INSILICO_HCE_COLUMNS)
