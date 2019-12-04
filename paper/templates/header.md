# Authors:
{% for author in authors -%}
{{ author.name }}{{ author.notes }} {{ author.email }}  
{% endfor %}

{% for institution in affiliations -%}
{{ institution|wordwrap }}   
{% endfor %}

\* Corresponding author
E-mail: {{ correspondance_email }} ({{ correspondance_initials }})
