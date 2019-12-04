{% extends 'va_compare_table.md' %}

{% block table_title -%}
Median chance-corrected concordance (%) for InsilicoVA and Tariff 2.0
{%- endblock %}

{% block caption -%}
Table {{table_num}} shows the median value and uncertainty interval across 500 test-train
splits using different probbase matrices for prediction, by age group, with and
without health care experience questions included. InSilicoVA was run without
training using the default probbase, with an empirical probbase derived from
training data mapped to the InterVA format, and with an empirical probbase
derived from training data mapped to the Tariff 2.0 format. Previously published
Tariff 2.0 results are shown for comparison.
{%- endblock %}
