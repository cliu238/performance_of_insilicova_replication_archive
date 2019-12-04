Abstract
========

### Background

Recently, a new algorithm for automatic computer certification of verbal autopsy data named InsilicoVA was
published. The authors present their algorithm as a statistical method and assess
performance using a single set of model predictors and age group.

### Methods

We perform a standard procedure for analyzing the predictive accuracy of verbal
autopsy classification methods using the same data and
the publicly available implementation of the algorithm released by the authors.
We extend the original analysis to include children and
neonates, instead of only adults, and test accuracy using different sets of
predictors, including the set used in the original paper and the set that
matches the released software.

### Results

The population-level performance (i.e. predictive accuracy) of the algorithm varied from {{tariff_min}} to
{{tariff_max}} when trained on data preprocessed similarly to the original study.
When trained on data that matched the software default format performance ranged
from {{insilico_min}} to {{insilico_max}}. When using the default training data
provided performance ranged from {{default_min}} to {{default_max}}.
Overall InSilicoVA predictive accuracy was found to be {{diff_lower}} to
{{diff_upper}} percentage points lower than an alternative algorithm.
Additionally, sensitivity for InSilicoVA was consistently lower than for an
alternative diagnostic algorithm (Tariff 2.0), although specificity was
comparable.


### Conclusions

The default format and training data provided
by the software lead to results that are at best suboptimal, with poor cause of
death predictive performance. This method is likely to generate erroneous cause of death predictions
and, even if properly configured, is not as accurate as alternative automated diagnostic
methods.

Keywords
========
{{keywords}}
