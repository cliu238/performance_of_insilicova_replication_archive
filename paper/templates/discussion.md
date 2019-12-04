Discussion
==========
As expected, InsilicoVA performed best when using the causes and symptoms that
closely matched the data. The differences between using the causes and symptoms
from the data versus mapping to the InterVA causes and symptoms was greatest for
neonates. The differences in population-level accuracy were generally larger
than at the individual level. Even when using the ideal configuration InSilicoVA
always had lower diagnostic accuracy than the Tariff 2.0 method. The difference
was greatest for adults where, without health care variables, the predictive accuracy of InSilicoVA was
{{diff_adult_ccc}} percentage points lower at the individual level, and
{{diff_adult_csmf}} percentage points lower at the population level. This poorer
performance, particularly for adult deaths, has significant
implications for estimating cause of death patterns in countries where, in all
cases, the vast majority of deaths occur among the in the adult population.
[@wang2016gbd2015]

We have reviewed InSilicoVA for two complementary purposes.
First, we assessed the performance of the InSilicoVA method as a diagnostic
algorithm for verbal autopsy. Second, InSilicoVA is a new piece of software
that potentially could be applied routinely into vital statistics systems for
deaths without physician certification.
Knowing that this is a potential use for this software,
it is obviously important that the method can be easily applied, and with
confidence about diagnostic accuracy, in settings with little technical and
statistical support. The
need for continuous vetting of model input parameters and verification of model
convergence is likely to be problematic in many countries, and likely to result
in low-quality cause of death statistics in countries where
there are insufficient resources to procure these services.

Compared with Tariff 2.0, we found that InSilicoVA performs significantly worse
in correctly predicting causes of death. We
were not able to identify any configuration of input parameters, for any age
group, that outperformed published estimates from the Tariff 2.0 algorithm.
InSilicoVA shows the most promising results for child and neonates, despite
having noticeably fewer symptom predictors for these age groups, but even for these age groups still has
noticeably lower diagnostic accuracy than Tariff 2.0. This result is generally
consistent when comparing cause-specific performance between the two algorithms.
For a few causes, InSilicoVA had higher CCC. However, the increased sensitivity
was at the expense of other causes, which had significantly lower concordance and
may indicate that the model overfits to causes which may be easier to detect.
This is especially evident for the neonate, where InSilicoVA achieved higher
concordance for four causes, but predicted the other two causes at level equal
to chance, as indicated by the uncertainty interval containing zero. This is in
contrast to Tariff 2.0, which performed similarly across causes, with the
exception of Stillbirth, which had high concordance for both algorithms.

To predict with this algorithm, users must decide what conditional probabilities
matrix to use. The InSilicoVA authors propose that, in practice, ranked conditional probabilities be
derived from expert panels that rank the propensities of seeing a symptom given
a particular cause of death. [@mccormick2016insilicova] They show that the
predictive accuracy of the method is heavily dependent on the quality
of this input. However, deriving these probabilities may not be straightforward.
The required value is the probability of a *respondent
saying* the decedent had a given symptom. This is subtly but importantly different from the
probability of the *decedent having* the symptom. The value needed for this
algorithm requires that a decedent had a symptom, the decedent communicates this
symptom to someone or someone notices it, the interviewer finds this person who
knew about the symptom, and the respondent remembers the
symptom months later when the VA interview is being conducted. The respondent may not
notice or may forget key symptoms.
When medical professionals create these ranked conditional probabilities,
they may implicitly estimate the probability of identifying a symptom themselves
in their expert, clinical evaluation. This value could mislead the algorithm and
result in inaccurate predictions. It is necessary that experts who select these
conditional probabilities balance both the presentation of symptoms due to a
disease and the ability of non-experts to reliably identify, remember, and report on these
symptoms.

We report here, for the first time, the predictive performance of InSilicoVA
using the default conditional probabilities (from InterVA). Given resource
constraints in the settings where VA is likely to be used, and the logistical
difficulties of collecting location-specific probbase information from medical
professionals familiar with the area, it is quite likely that the InSilicoVA defaults
will be used in practice. We found that the default configuration and
conditional probabilities consistently perform worse than chance at all
ages at the population-level.
The authors claim that InSilicoVA is applicable in a wider range of setting
because it does not need to rely on "gold standard" data. [@mccormick2016insilicova] However, we have demonstrated that
using expert-derived training as opposed to empirically derived training data results
in unacceptably poor performance.

The results from this study match a previous
validation of the InterVA algorithm, which found that, once corrected for chance,
population-level accuracy of predictions using an expert-derived probbase, are
relatively poor. [@lozano2011interva] The InterVA probbase used by
InSilicoVA has undergone extensive field testing and review by numerous
investigators in multiple countries. [@byass2012interva4] Given this, we believe
it is extremely unlikely for expert-derived probbases to produce estimates
that rival empirically derived training such as that used by Tariff 2.0.
Additionally, expert-derived training has the unfortunate effect of often
appearing plausible since it reconfirms the intuition of the experts
training and evaluating the method, which can be, and often is, incorrect.
The net result is a situation in which
diagnostic information being provided by InSilicoVA is likely to be worse than acting on no information
whatsoever.

In this study, we used test data with a cause distribution uncorrelated with the
training data. This resulted in scenarios in which the training data and test
data were sufficiently different that the model could not successfully converge. The
`R` package displays a warning about non-convergence and says the results may be
unreliable, but still yields outputs. This raise two operational considerations with the use of InSilicoVA.
First, it is possible to create a conditional probabilities matrix in which the
model does not successfully produce reliable results. Second, the `R` package
produces results even in this circumstance. It is possible that InSilicoVA users
may unintentionally overlook the warning that Markov-chain Monte Carlo process has not converged, leading to
adoption of results which are known to be statistical inaccurate.

Installing `Java` and properly configuring `R` and `Java` to work together
requires considerable technical expertise and is not standardized across
different computer systems. Although InSilicoVA is freely available, it may
require expert technical consultation to be usable.

Conclusions
===========

Verbal autopsy as a diagnostic method is now being actively considered by countries for
routine widespread use in surveillance and vital statistics systems. [@lopez201health_intel] It is
important to keep improving the science behind estimation and validation of
different cause of death prediction strategies so that policy makers can be
provided the highest quality estimates based on the best possible measurement methods. It is also important that methods be
independently investigated and evaluated for usability for governments in low
and middle-income countries seeking to reduce ignorance about who dies of what.

The InSilicoVA algorithm provides some key advances in CCVA. Unlike previous
algorithm, it provides a method for calculating the uncertainty in each
prediction. However, implementing the algorithm effectively requires both an
increased level of technical expertise to utilize `R` and `Java` and conceptual
expertise to tune model hyperparameters and interpret convergence from a
hierarchical Bayesian model. Additionally, our results indicate that the default
setting for conditional probabilities that come with the `R` package is
suboptimal. This means that users should be very cautious about applying this new
method.

Moreover, in the validation environment we have defined using the PHMRC
database, InSilicoVA was found to be less accurate than Tariff 2.0
in predicting both causes of death for individuals (by about 10% in CCC) and the cause
of death distribution in a population (about 20% less accurate in CCCSMF), with the
differences being more marked for adult and child death deaths than for neonates.  For 20 out of 61 causes of death, InSilicoVA was found to have higher sensitivity than Tariff 2.0 (when both were run without healthcare experience), while for 40 the sensitivity was lower.
Since the vast majority of deaths in low and middle income countries now occur
among children and adults, rather than neonates, the higher CCCSMF Accuracy
of Tariff 2.0 in predicting  causes of death, along with its ease of
application, should make it the method of choice for countries seeking to
maximize the accuracy and cost-effectiveness of automated verbal autopsy in
their national CRVS systems.
