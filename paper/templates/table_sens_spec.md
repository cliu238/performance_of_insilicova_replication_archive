##### Table {{ table_num }}: {% block table_title %}Median sensitivity and specificity (%) for InsilicoVA and Tariff 2.0{% endblock %}

|         |        |InSilicoVA (Tariff 2.0 Training)||           Tariff 2.0           ||
|:-------:|:------:|:------------------:|:------------------:|:------------------:|:------------------:|
|         |        | Median Sensitivity | Median Specificity | Median Sensitivity | Median Specificity |
|  Adult  | No HCE |{% for med in adult_no_hce %} {{med|center(18)}} |{% endfor %}
|         |   HCE  |{% for med in adult_hce %} {{med|center(18)}} |{% endfor %}
|  Child  | No HCE |{% for med in child_no_hce %} {{med|center(18)}} |{% endfor %}
|         |   HCE  |{% for med in child_hce %} {{med|center(18)}} |{% endfor %}
| Neonate | No HCE |{% for med in neonate_no_hce %} {{med|center(18)}} |{% endfor %}
|         |   HCE  |{% for med in neonate_hce %} {{med|center(18)}} |{% endfor %}

{% block caption -%}
Table {{ table_num }} shows the sensitivity and specificity across causes for
InSilicoVA using an empirical probbase derived from training data mapped to the
Tariff 2.0 format. Previously published Tariff 2.0 results are shown for
comparison.
{% endblock %}