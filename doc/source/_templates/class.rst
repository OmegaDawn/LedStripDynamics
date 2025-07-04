{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}
.. inheritance-diagram:: {{ name }}
   :include-subclasses:
   :parts: 1

.. autoclass:: {{ objname }}
   :members:
   :inherited-members:
   :show-inheritance:
   :undoc-members:


   {% block methods %}
   .. automethod:: __init__


   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ _('Attributes') }}
   .. autosummary::
   {% for item in attributes %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}


   {% if properties %}
   .. rubric:: {{ _('Properties') }}
   .. autosummary::
   {% for item in properties %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
   {% endif %}


   {% if methods %}
   .. rubric:: {{ _('Methods') }}
   .. autosummary::
   {% for item in methods %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}
