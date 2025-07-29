{% macro get_semantic_model_config(model_name) %}
  {#- Get the semantic model configuration for a given model name -#}
  
  {%- set semantic_model_config = none -%}
  
  {#- First try to find semantic models in the graph.nodes -#}
  {%- if graph.nodes -%}
    {%- for node_id, node in graph.nodes.items() -%}
      {%- if node.resource_type == 'semantic_model' and node.name == model_name -%}
        {%- set semantic_model_config = node -%}
        {%- break -%}
      {%- endif -%}
    {%- endfor -%}
  {%- endif -%}
  
  {#- If not found in nodes, try to look in graph itself for semantic_models -#}
  {%- if not semantic_model_config -%}
    {%- if graph.get('semantic_models') -%}
      {%- for semantic_model_id, semantic_model in graph.semantic_models.items() -%}
        {%- if semantic_model.name == model_name -%}
          {%- set semantic_model_config = semantic_model -%}
          {%- break -%}
        {%- endif -%}
      {%- endfor -%}
    {%- endif -%}
  {%- endif -%}

  {#- If still not found, return none -#}
  {{ return(semantic_model_config) }}

{% endmacro %} 