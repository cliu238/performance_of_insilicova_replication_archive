Validation
==========

We follow the procedure in Murray et al. for validating verbal autopsy methods.
[robust_metrics]_


.. graphviz::

    digraph foo {
       "Original Data" -> "Split";
       "Split" -> "Test Pool";
       "Split" -> "Train Data";
       "Test Pool" -> "Resample";
       "Dirichlet CSMF" -> "Resample";
       "Resample" -> "Test Data";
       "Test Data" -> "Statistic";
       "Train Data" -> "Statistic";
    }


Splitting
---------

.. autofunction:: validation.config_model_selector

.. autofunction:: validation.config_sss_model_selector

.. autofunction:: validation.config_holdout_model_selector


Resample
--------

.. autofunction:: validation.dirichlet_resample


Prediction
----------

.. autofunction:: validation.prediction_accuracy

.. autofunction:: validation.out_of_sample_accuracy

.. autofunction:: validation.in_sample_accuracy

.. autofunction:: validation.no_training_accuracy
