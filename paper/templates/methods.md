Methods
=========
Algorithm
---------
InSilicoVA [@mccormick2016insilicova] is a Bayesian framework that improves upon
InterVA [@byass2003interva] by
using information about symptoms that are, and are not endorsed, to
estimate probabilities for each cause of death in a way that is comparable across observations,
and by estimating
the individual-level and population-level predictions simultaneously.
The model is estimated using Markov-Chain Monte-Carlo (MCMC) simulations. To
produce usable results, the algorithm must run a sufficient number of samples to
ensure convergence.
The authors have released their algorithm as an `R` package, with
computationally intensive MCMC calculation implemented in Java through the
`rJava` package. The algorithm utilizes a matrix of conditional probabilities
between each cause and each symptom. These propensities, which the authors call
the *probbase*, capture the user's initial estimate of the relative likelihood
of a symptom being endorsed for a given cause of death. These estimates can be derived from
data or from expert judgement. The `R` package allows the user to input their own
probbase file and also provides a default probbase based on the InterVA project.
Open-source code (licensed under the GNU Public License version 2) for the `R`
implementation of InSilicoVA is freely available online.

Data
----
We used the publicly available Population Health Metrics Research Consortium
(PHMRC) gold standard database [@murray2011phmrc_gsva; @phmrc_gs_data] to validate the InSilicoVA
algorithm. This dataset contains verbal autopsies matched to cause of death
diagnoses from medical records, with variable confidence.
Cases in the dataset were initially identified from deaths
in hospitals where strict, pre-determined diagnostic criteria were satisfied.
This ensured that the true cause of death was known with greater certainty than
is often the case for deaths recorded in vital registration systems where
diagnostic misclassification is typically estimated to range between 30 and 60 percent. [@rampatige2014systematic;
@khosravi2008misclassification] After identifying cases, blinded verbal autopsies were collected
using a modified version of the WHO verbal autopsy instrument. This resulted in
a validation database of {{n_records}} records for which the true cause of
death was known with reasonable certainty, and for which a full verbal autopsy
interview had been conducted.

Verbal autopsies were collected from six sites in four different
countries: Andhra Pradesh, India; Bohol, Philippines; Dar
es Salaam, Tanzania; Mexico City, Mexico; Pemba Island, Tanzania; and Uttar
Pradesh, India between 2007 and 2010. The database includes deaths from
{{n_adult}} adults, {{n_child}} children, {{n_neonate}} neonates and
{{n_stillbirth}} stillbirths. Following practice from previous research, we used the most
aggregated cause list with 34 adult causes, 21 child causes and 6 neonate causes
(including stillbirth) to assess accuracy of cause of death predictions. These
cause of death lists are shown in Additional file 1.

Validation Framework
--------------------
In this study, we follow the recommendations of Murray et al. for
validating verbal autopsy diagnostic methods. [@murray2011metrics] For
this procedure, the validation dataset is randomly divided into a train fold
containing 75% of the observations and a test fold containing the remaining 25% of
observations. This is repeated 500 times, resulting 500 test-train sets, each with a
different subset of the original observations. For each test-train set,
any given record appears in either the train set
or the test set, but not both. The test set is then resampled to an uninformative
Dirichlet distribution. This ensures that the cause composition of the train and
test sets are uncorrelated which provides a more robust measure of
performance (for example, it prevents naive prediction algorithm from guessing an accurate
population level distribution without utilizing information at the individual level).
Additionally, because the cause composition varies substantially across the 500
test-train splits, it ensures that the algorithm is tested on datasets
with a wide variety of cause distributions and performance estimates are not
skewed by overfitting to the most common cause in the training data.
To assess performance at the
individual level, we use the median chance-corrected concordance (CCC) across
causes. [@murray2011metrics] To assess performance at the population level we
use chance-corrected cause-specific mortality fraction accuracy (CCCSMF).
[@flaxman2015cccsmf] Chance-corrected concordance for a single cause is
calculated as:

$$CCC_j = \frac{ \frac{TP_j}{TP_j + FN_j} - \frac{1}{N}}{1 - \frac{1}{N}}$$

where $TP_j$ is the number of true positives for cause $j$, $TN_j$ is the number
of true negatives and $N$ is the number of causes. Values range between -1.0 and
1.0 where 1.0 indicates perfect ability to detect (i.e. diagnose) a cause, 0.0 indicates random
guessing, and negative 1.0 indicates no ability to detect a cause.
To create an overall metric of individual-level prediction
accuracy, we use the mean of the cause-specific CCCs. Cause-specific mortality
fraction (CSMF) accuracy is calculated as:

$$\mathrm{CSMF Accuracy} = 1 - \frac{\sum_{j=1}^k |\mathrm{CSMF}_j^{\mathrm{true}}-\mathrm{CSMF}_j^{\mathrm{pred}}|}
                     {2 \left(1 - \min_j \left(\mathrm{CSMF}_j^{\mathrm{true}}\right)\right)}$$

where $\mathrm{CSMF}_j^{\mathrm{true}}$ is the true fractions for cause $j$ and
$\mathrm{CSMF}_j^{\mathrm{pred}}$ is the predicted fraction for cause $j$. This
statistic can be corrected for chance (see Flaxman et al. [@flaxman2015cccsmf]);
we calculate chance-corrected CMSF Accuracy as:

$$\mathrm{CCCSMF Accuracy} = \frac{\mathrm{CSMF Accuracy} - (1 - e^{-1})}{1 - (1 - e^{-1})}$$

Similarly to CCC, perfect CCCSMF Accuracy is attained at value 1.0, and values
near 0.0 indicate that the diagnostic procedure being applied is essentially equivalent to random guessing.

InSilicoVA Validation
---------------------
The InSilicoVA `R` package allows for a range of customizations to the inputs
used to predict the cause of death. We validate the algorithm using three
different configurations of inputs to assess its usability and performance.
These configurations are: 1) using the built-in default training data, 2)
training the algorithm with inputs that resemble the defaults, and 3) training
the algorithm with inputs that do not resemble the defaults. Following the
practice established in Murray et al., we also conduct the analysis without
predictors derived from questions related to previous contact with the health
care system. This produces estimates of diagnostic accuracy that could be more
appropriate for generalizing to community deaths where decedents had no medical contact.
[@phmrc_gs_data] For each of the three
configurations we test all three age groups both with and without health care
experience questions.

**With default probbase:**

The default configuration assumes the input data matches the InterVA4 format
with 245 symptoms. It uses the conditional probabilities from InterVA to
predict one of 60 causes. With the default configuration, no
ancillary training data is required. To validate the default configuration, we
mapped the PHMRC database to the InterVA format, and then we used InSilicoVA to
predict the cause of death. We then mapped the predicted causes to the PHMRC
gold standard list. We compared these mapped predictions to the known underlying
cause as listed in the PHMRC database to calculate performance. Since the
algorithm was not trained empirically with this configuration, we used the
entire validation dataset to test the predictive performance. However, it is
still essential to test the algorithm on datasets with different cause
compositions, so we repeated this process on 500 test datasets, each with a
cause composition drawn from an uninformative Dirichlet distribution and samples
drawn from the complete dataset with replacement according to this cause
composition. The predicted causes included {{n_adult_causes}} adult causes of death
{{n_child_causes}} child causes, and {{n_neonate_causes}} neonate causes.
Of the 245
symptom predictors used by InSilicoVA, the PHMRC dataset contained data for
{{n_adult_i_symptoms}} adult symptoms, {{n_child_i_symptoms}} child symptoms and
{{n_neonate_i_symptoms}} symptoms for neonates.

**With empirical probbase:**

Next, we assessed how InSilicoVA performed with training data that matched its
expected inputs. For this assessment, we mapped the PHRMC database to the
InterVA symptoms and the 'gold standard' causes were mapped to the predicted causes. For
each of the 500 test-train splits, we used the train split to calculate the
empirical probability of an InterVA symptom being endorsed, conditional on the
mapped cause. This conditional probabilities matrix was used as the input probbase
for the algorithm. The test split was resampled to a Dirichlet cause distribution
and the algorithm predicted a cause from the default set of causes.

**With empirical probbase matching Tariff 2.0:**

Finally, we assessed how the algorithm performed with training data of a
different format than the standard inputs. For this assessment, the PHMRC
database was mapped to the set of symptoms used by the Tariff 2.0
algorithm. [@serina2015tariff2] Data were mapped to {{n_adult_t_symptoms}} adult
symptoms, {{n_child_t_symptoms}} child symptoms, and {{n_neonate_t_symptoms}}
neonate symptoms. For each of the 500 test-train splits, we used the train split
to calculate the empirical probability of a Tariff 2.0 symptom being endorsed
conditional on the original PHMRC gold standard cause. We then used this
empirical probability matrix in the InSilicoVA algorithm to predict
causes of death. As before, we predicted for data in the test split after it had been resampled to a Dirichlet
cause distribution. Of the three assessments, this configuration should be the
most favorable towards InSilicoVA since it avoids any possible discrepancies
between definitions of the PHMRC causes and the default causes, and provides more
symptom predictors for the algorithm to use.

The InSilicoVA `R` package provides {{n_hyperparam}} hyperparameters, which allow
users to tune the estimation procedure. Except where specifically mentioned, we
used the default value provided by the InSilicoVA packages. The validity of the
results depends on the Monte Carlo experiment successfully converging to a stable
result. We repeated each experiment using three times the default number of
simulations and assessed the number of splits that converged and any differences
in the results. Convergence was assessed using the Heidelberger and Welch test
included with the `R` package. We used the `extract.prob` function
provided by the InSilicoVA package in all training exercises.
