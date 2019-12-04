Research in Context
===================

Evidence before this study
--------------------------

Previous research on this topic fall into two categories. The first involves
methodological research into the appropriate ways to validate algorithms used to
predict causes of death from verbal autopsy data. This involves development and
selection of the correct statistics for measuring accuracy and determining what
are the most useful comparisons. There are two widely used option. The
predictions from algorithms are either compared to guesses made by physicians
reviewing the same verbal autopsy or to labeled validation data in which a
medical autopsy was paired with an accompanying, blinded verbal autopsy. The
first yields only a concordance measure. Additionally, it has been shown that
physician's diagnoses using verbal autopsy has lower accuracy than that of
algorithms when the true underlying cause is known. The second option has been
criticized for both its generalizability, since it relies primarily on hospital
deaths where there are high-quality diagnostics, and for its prohibitive costs.
Neither our study nor the study we are reviewing attempt to make methodological
improvements into the validation procedure. Once we establish a set of
standardized criteria for determining performance, the second type of research
involves finding a mathematical model which performs best and then compare it to
existing models. The InSilicoVA improves upon the InterVA algorithm which has
been used, primarily at demographic surveillance sites, for over a decade.
Previous research, including the original InSilicioVA publication, found an
alternative algorithm, Tariff 2.0, consistently performs better InterVA. As such
it seems prudent to compare the new InSilicoVA algorithm to the highest
performing existing algorithm.

Added value of this study
-------------------------

Our study provides independent replication of the InSilicoVA algorithm and
extends the validation to look include child and neonate age groups, which are
populations of interest for the global health community. Additionally, we
validate the method using the default settings and format for the published
software and compare it to the results from the initial validation. Researchers
and health systems practitioners are likely to use software released by the
original authors "as is" which makes it important to understand the performance
of the defaults.


Implications of all available evidence
--------------------------------------

Contrary to the original publication, we found that the algorithm, as
implemented in the released software package, does not perform better than the
leading alternative algorithm. Additionally, the default configuration performs
significantly worse than the optimal configuration presented in the original
publication. This suggest more investigation is required before InSilicoVA is
suitable for widespread use.
