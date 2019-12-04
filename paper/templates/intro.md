Background
==========
Reliable population-level causes-of-death estimates are critically important for
designing effective public health policies. [@phillips2015crvs] Verbal autopsy
is a key component of enhancing health information systems in many countries
that do not have reliable civil registration and vital statistics systems.
[@sankoh2014cr_w_va; @boerma2014cod_registation] Verbal autopsy consists of a
structured interview with family members of the deceased with the purpose of
gathering enough information to infer the likely cause of death.
[@soleman2006va_practices] In some countries where up to 80-90% percent of deaths
occur without medical attendance, verbal autopsy provides the only usable
information for generating population-level cause of death estimates with reasonable and
representative coverage. [@abouzahr2015crvs_data] Computer algorithms that can reliably
assign a cause of death greatly increase the feasibility of integrating VA routinely into
CRVS systems. Computer certification of verbal autopsy (CCVA) allows systems to be
scalable, consistent, and sustainable. [@deSavigny2017va_into_crvs]

Numerous algorithms for predicting the cause of death from verbal autopsies have
been developed over the last decade. [@serina2015tariff2; @flaxman2011king_lu;
@murray2007ssp; @byass2003interva; @flaxman2011random_forest] We previously
developed a framework for validating the predictive accuracy of different diagnostic methods
that allows for direct
comparison of methods using the same standard set of criteria. [@murray2011metrics] It provides a way
of determining how well an algorithm will perform in different populations when
the true distribution of causes of death is not known. This is crucial for
generalizing results to new study populations and accurately capturing unknown
changes in cause of death composition in the same population across time. We
have used this procedure to determine the accuracy of a wide range of previously
developed methods. [@murray2014horserace]

Recently a new algorithm for CCVA called *InSilicoVA* was developed and
published. [@mccormick2016insilicova] This method builds off previous research
on the InterVA algorithm, and advances the approach by introducing an algorithm
that quantifies uncertainty in the
individual-level predictions and uses this information to better predict the
cause distribution at the population-level. This aligns well with the current
global interest in using VA to estimate the distribution of causes of death for
populations through routine application in vital registration systems.
The authors use a range of metrics to determine the performance
of their algorithm, including applying our assessment framework. However, the authors only
validated the results for adult deaths and not child or neonatal deaths.
Moreover, given the potential of such methods for transforming knowledge about
cause of death patterns in populations for which little is currently known about
the leading causes of death,
we believe that an independent validation of their results is warranted, before
the method can be recommended for routine application.

In this study, we assess the diagnostic accuracy of the InSilicoVA
algorithm for all ages using the same validation environment as used in the
original InSilicoVA paper, namely the Population Health Metric Research
Consortium (PHMRC) gold standard database. We applied the validation procedure
developed by Murray et al
[@murray2011metrics] and assessed performance at the individual-level, using
chance-corrected concordance (CCC), and at the population-level, using
chance-corrected cause-specific mortality fraction (CCCSMF) accuracy.
