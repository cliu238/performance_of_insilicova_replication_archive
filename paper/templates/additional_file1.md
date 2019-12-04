Additional file 1
=================

List of causes of death from the Population Health Metric Research Consortium
database and mapping to causes used by InsilicoVA.

Adult causes
------------

The more detailed list of 46 causes was used to map PHMRC causes to the
InSilicoVA causes. This provides better matching of some causes, especially for
maternal causes. Analyses using PHMRC causes used the more aggregated list of
34 causes.

| ICD 10 |             PHMRC Cause 46         |             PHMRC Cause 34         |           InSilicoVA Cause         |
|:-------|:-----------------------------------|:-----------------------------------|:-----------------------------------|
{% for icd, c46, c34, interva in adult -%}
    |{{icd.ljust(8)}}|{{c46.ljust(36)}}|{{c34.ljust(36)}}|{{interva.ljust(36)}}|
{% endfor %}

Child causes
------------

| ICD 10 |             PHMRC Cause            |           InSilicoVA Cause         |
|:-------|:-----------------------------------|:-----------------------------------|
{% for icd, phmrc, interva in child -%}
    |{{icd.ljust(8)}}|{{phmrc.ljust(36)}}|{{interva.ljust(36)}}|
{% endfor %}

Neonate causes
--------------

| ICD 10 |             PHMRC Cause            |           InSilicoVA Cause         |
|:-------|:-----------------------------------|:-----------------------------------|
{% for icd, phmrc, interva in neonate -%}
    |{{icd.ljust(8)}}|{{phmrc.ljust(36)}}|{{interva.ljust(36)}}|
{% endfor %}
