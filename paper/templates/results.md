Results
=======
Tables {{table_ccc}} and {{table_cccsmf}} show the algorithmic
performance of InSilicoVA at the individual level and population level,
respectively, using the default probbase, training the algorithm on data with
the same causes and symptoms as the default probbase, and training the algorithm
on data with different causes and symptoms. At both the individual level and the
population level, the configuration using the causes published with the dataset
and the Tariff 2.0 symptoms performed best across all age groups regardless of
whether health care experience (HCE) variables were included. These variables
are intended to reflect the impact of the extent of contact with health services
prior to death in terms of additional information that might improve diagnostic
accuracy.

At the individual level, InSilicoVA performed best for predicting the
cause of death for child deaths. Without HCE variables, the median CCC for child
VAs was {{default_child_ccc['value']}} (UI {{default_child_ccc['lb']}},
{{default_child_ccc['ub']}}) using the default probbase,
{{insilico_child_ccc['value']}} (UI {{insilico_child_ccc['lb']}},
{{insilico_child_ccc['ub']}}) when training the algorithm on the default cause list
and symptoms, and {{tariff_child_ccc['value']}} (UI {{tariff_child_ccc['lb']}},
{{tariff_child_ccc['ub']}}) when using the causes and symptoms which best
matched the data. For adults and neonates, InSilicoVA performed substantially
worse with the default probbase than with the Tariff 2.0 causes and symptoms.
The CCC for adults was {{default_adult_ccc['value']}}
(UI {{default_adult_ccc['lb']}}, {{default_adult_ccc['ub']}}) using the defaults
and {{tariff_adult_ccc['value']}} (UI {{tariff_adult_ccc['lb']}},
{{tariff_adult_ccc['ub']}}) using Tariff 2.0 causes and symptoms. The CCC for
neonates was {{default_neonate_ccc['value']}} (UI {{default_neonate_ccc['lb']}},
{{default_neonate_ccc['ub']}}) using the defaults and
{{tariff_neonate_ccc['value']}} (UI {{tariff_neonate_ccc['lb']}},
{{tariff_neonate_ccc['ub']}}) using the Tariff 2.0 causes and symptoms. For
adults, training the algorithm using the default causes and symptoms yielded
diagnostic accuracy very similar to that resulting from using Tariff 2.0 causes and symptoms,
{{insilico_adult_ccc['value']}} (UI {{insilico_adult_ccc['lb']}},
{{insilico_adult_ccc['ub']}}) compared to {{tariff_adult_ccc['value']}}
(UI {{tariff_adult_ccc['lb']}}, {{tariff_adult_ccc['ub']}}). For neonates,
training using default symptoms and causes produced lower CCC,
{{insilico_neonate_ccc['value']}} (UI {{insilico_neonate_ccc['lb']}},
{{insilico_neonate_ccc['ub']}}) compared to {{tariff_neonate_ccc['value']}}
(UI {{tariff_neonate_ccc['lb']}}, {{tariff_neonate_ccc['ub']}}) when training using
the Tariff 2.0 symptoms. The cause-specific performance, as measured by
chance-corrected concordance varied significantly by cause. Tables {{table_adult_ccc}}
to {{table_neonate_ccc}} summarize the cause-specific chance-corrected
concordance. When the model was trained using Tariff 2.0 symptoms, the adult
causes with the highest CCC were  {{', '.join(adult_high_ccc_causes)}}; the child
causes with the highest CCC were {{', '.join(child_high_ccc_causes)}}; and the
neonate causes with the highest CCC were {{', '.join(neonate_high_ccc_causes)}}.
Across all age groups, {{n_rand_ccc}} causes were predicted at or below the
level of random guessing.  Additional files 2 to 4 present the full
misclassification matrix for cause-specific performance of InSilicoVA
when trained using Tariff 2.0 symptoms, and predicted without
healthcare experience, to show the detailed patterns of prediction at
the individual level.

At the population level, InSilicoVA performed best in predicting the CSMF for
neonates when provided with training data. The algorithm performed substantially
worse than chance for all age groups using the default probbase, despite
predicting better than chance at the individual level for adults and children.
The median CCCSMF was {{default_adult_cccsmf['value']}}
(UI {{default_adult_cccsmf['lb']}}, {{default_adult_cccsmf['ub']}}) for adults,
{{default_child_cccsmf['value']}} (UI {{default_child_cccsmf['lb']}},
{{default_child_cccsmf['ub']}}) for children and
{{default_neonate_cccsmf['value']}} (UI {{default_neonate_cccsmf['lb']}},
{{default_neonate_cccsmf['ub']}}) for neonates. The median CCCSMF is higher for
child and neonate age groups when using the Tariff 2.0 causes and symptoms.
For adults, the performance is the same when using the InterVA or Tariff 2.0
training. The CCCSMF was
{{tariff_adult_cccsmf['value']}} (UI {{tariff_adult_cccsmf['lb']}},
{{tariff_adult_cccsmf['ub']}}) for adults, {{tariff_child_cccsmf['value']}}
(UI {{tariff_child_cccsmf['lb']}}, {{tariff_child_cccsmf['ub']}}) for children and
{{tariff_neonate_cccsmf['value']}} (UI {{tariff_neonate_cccsmf['lb']}},
{{tariff_neonate_cccsmf['ub']}}) neonates.

At both the individual level
and the population level, Tariff 2.0 outperforms InSilicoVA in all age groups.
At the individual level without HCE variables, the median CCC across splits was
{{diff_adult_ccc}} percentage points higher for adults, {{diff_child_ccc}}
percentage points higher for children and {{diff_neonate_ccc}} percentage points
higher for neonates using Tariff 2.0 to diagnose the VAs, compared to InSilicoVA.
At the population level, the median CCCSMF for Tariff 2.0
was {{diff_adult_cccsmf}} percentage points higher for adults,
{{diff_child_cccsmf}} percentage points higher for children and
{{diff_neonate_cccsmf}} percentage points higher for neonates. Figure 1 shows
the individual level and population level performance of InSilicoVA using
different configuration compared to Tariff 2.0. The cause-specific performance
of InSilicoVA tended to follow a similar pattern as the Tariff 2.0 algorithm
when trained using the same symptoms as predictors, except that Tariff 2.0
concordance was generally higher. Across all age groups, InSilicoVA had higher
concordance only for {{', '.join(higher_ccc_adult)}} in adults,
{{', '.join(higher_ccc_child)}} in children and
{{', '.join(higher_ccc_neonate)}} in neonates.

Across all age groups, InSilicoVA had higher sensitivity for {{n_insilico_higher_sens}} of {{n_phmrc_causes}} PHMRC
causes for at least one of the with HCE/without HCE scenarios.
It had higher specificity for {{n_insilico_higher_spec}} of {{n_phmrc_causes}}
PHMRC causes. Table 6 shows the median sensitivity and specificity across cause
for InSilicoVA and Tariff 2.0. Overall Tariff 2.0 had higher sensitivity for all
age groups with and without the health care experience predictors. InSilicoVA
had comparable specificity to Tariff 2.0 for adults and children, but slightly
lower specific for neonates.
Additional file 5 shows cause-specific comparisons of InSilicoVA and
Tariff 2.0 using sensitivity and specificity.

Further, when using training data, the model did not always converge for every test-train
split. Across the three modules and different mappings of training data,
{{pct_unconverged_lower}} to {{pct_unconverged_upper}} of the 500 test-train
splits the model did not converge when using the default number of Monte Carlo
simulations. We increased the number of simulations performed during the fitting process to
three times the default to see of the model would eventually converge. Even with these
extra samples, up to {{pct_unconverged_lower_ext}} splits still failed to converge for some
configurations.

##### Figure 1: Comparison of InSilicoVA and Tariff 2.0 at the individual and population levels.
Note: Individual-level accuracy is assessed using chance-correct concordance.
Population-level accuracy is assessed using chance-corrected cause-specific
mortality fraction (CSMF) accuracy. Values of zero in either dimension are
equivalent to random guessing and range up to 100% for perfect accuracy.
InSilicoVA is tested using the default expert-derived probbase, a probbase
empirically trained using InterVA symptoms, and a probbase empirically trained
using Tariff 2.0 symptoms. Published accuracies of Tariff 2.0 are shown for
comparison.
