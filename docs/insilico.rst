InSilicoVA
==========

This module provides a python wrapper around the R package. The module exposes
a single class, which is loosely based off of the sklearn estimators objects.
This class is not completely compatible with other sklearn classifiers for two
reasons:

1. The ``InsilicoClassifier`` requires ``pandas.NDFrame`` objects (dataframes
   and series) instead of ``numpy.array`` objects. The column and index labels
   are used to validate the data transfer between python and R.
2. The ``predict`` method returns a tuple of individual-level predictions and
   population-level predictions. The two series are simultaneously estimated
   using a hierarchical Bayesian framework so it is not possible to simply
   aggregate the individual-level predictions to derive the population-level
   estimates.

The primary interface, like sklearn classifiers, centers around two methods:
``fit`` and ``predict``. These can be chained in typical sklearn fashion:
``clf.fit(X_train, y_train).predict(X_test)``. There are lower level methods
which provide wrappers around the R functions. These are ``extract_prob``, for
fitting, and ``insilico_fit``, which predicts. These methods provide some input
and output validation and transformation, as well as standardizing parameter
names to snake-case. Lastly, direct access to the rpy2 converted functions is
available from the converted R package which is loaded when the classifier is
instantiated.

.. autoclass:: insilico.InsilicoClassifier

.. raw:: html

    <iframe src="_static/r_help/r_insilico.html"
            height="600px" width="100%"></iframe>

Getters
-------
.. automethod:: insilico.InsilicoClassifier.get_r_insilico_package

.. raw:: html

    <iframe src="_static/r_help/r_package.html"
            height="635px" width="80%" style="margin-left:10%"></iframe>

.. automethod:: insilico.InsilicoClassifier.get_sample_data

.. raw:: html

    <iframe src="_static/r_help/r_randomva1.html"
            height="450px" width="80%" style="margin-left:10%"></iframe>

.. automethod:: insilico.InsilicoClassifier.get_cond_prob_num

.. raw:: html

    <iframe src="_static/r_help/r_condprobnum.html"
            height="365px" width="80%" style="margin-left:10%"></iframe>

.. automethod:: insilico.InsilicoClassifier.get_insilico_causes

.. automethod:: insilico.InsilicoClassifier.get_insilico_symptoms

.. automethod:: insilico.InsilicoClassifier.get_insilico_short_causes

.. raw:: html

    <iframe src="_static/r_help/r_cause_text.html"
            height="365px" width="80%" style="margin-left:10%"></iframe>


Training
--------
.. automethod:: insilico.InsilicoClassifier.fit

.. automethod:: insilico.InsilicoClassifier.extract_prob

.. raw:: html

    <iframe src="_static/r_help/r_extract_prob.html"
            height="600px" width="85%" style="margin-left:10%"></iframe>

Predicting
----------
.. automethod:: insilico.InsilicoClassifier.predict
