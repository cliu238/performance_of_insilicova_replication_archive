##### Table {{ table_num }}: {% block table_title %}Median {{ module }} cause-specific chance-corrected concordance (%) for InsilicoVA and Tariff 2.0{% endblock %}

|                                      |      |                 InSilicoVA (Tariff 2.0 Training)                 ||||                           Tariff 2.0                           ||||
|:-------------------------------------|:----:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|
|                                      |      |     No HCE     |                |      HCE       |                |     No HCE     |                |      HCE       |                |
| PHMRC Cause                          |ICD10 |     Median     |     95% UI     |     Median     |     95% UI     |     Median     |     95% UI     |     Median     |     95% UI     |
{% for cause, icd, row in data -%}
  |{{cause.ljust(38)}}|{{icd|center(6)}}|{%- for d in row -%}{{d|center(16)}}|{% endfor %}
{% endfor %}

{% block caption -%}
Table {{ table_num }} shows the cause-specific chance-corrected concordance for
{{ module.lower() }} data for InSilicoVA using an empirical probbase derived from
training data mapped to the Tariff 2.0 format. Previously published Tariff 2.0
results are shown for comparison.
{% endblock %}