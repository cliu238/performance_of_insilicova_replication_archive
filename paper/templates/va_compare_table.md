##### Table {{ table_num }}: {% block table_title %}description{% endblock %}

|         |        |{% for clf in clfs %}|{{ clf|center(20) }}|{% endfor %}
|:-------:|:------:|{% for clf in clfs %}:--------:|:---------------:|{% endfor %}
|         |        |{% for clf in clfs %}  Median  |      95% UI     |{% endfor %}
|  Adult  | No HCE |{% for med, ui in adult_no_hce %} {{med|center(8)}} | {{ui|center(15)}} |{% endfor %}
|         |   HCE  |{% for med, ui in adult_w_hce %} {{med|center(8)}} | {{ui|center(15)}} |{% endfor %}
|  Child  | No HCE |{% for med, ui in child_no_hce %} {{med|center(8)}} | {{ui|center(15)}} |{% endfor %}
|         |   HCE  |{% for med, ui in child_w_hce %} {{med|center(8)}} | {{ui|center(15)}} |{% endfor %}
| Neonate | No HCE |{% for med, ui in neonate_no_hce %} {{med|center(8)}} | {{ui|center(15)}} |{% endfor %}
|         |   HCE  |{% for med, ui in neonate_w_hce %} {{med|center(8)}} | {{ui|center(15)}} |{% endfor %}

{% block caption %}caption{% endblock %}