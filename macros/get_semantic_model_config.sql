{% macro get_semantic_model_config(model_name) %}
  {#- Get the semantic model configuration for a given model name -#}
  
  {%- set semantic_models = [] -%}
  
  {#- Look through all sources to find semantic models -#}
  {%- for node in graph.sources.values() -%}
    {%- if node.resource_type == 'semantic_model' and node.name == model_name -%}
      {%- do semantic_models.append(node) -%}
    {%- endif -%}
  {%- endfor -%}
  
  {#- Also check in the current project's manifest for semantic models -#}
  {%- if project_name in graph.semantic_models -%}
    {%- for semantic_model_name, semantic_model in graph.semantic_models[project_name].items() -%}
      {%- if semantic_model.name == model_name -%}
        {%- do semantic_models.append(semantic_model) -%}
      {%- endif -%}
    {%- endfor -%}
  {%- endif -%}
  
  {#- Alternative approach: look in the manifest directly -#}
  {%- set ns = namespace(found_model=none) -%}
  {%- for semantic_model_id, semantic_model in graph.semantic_models.items() -%}
    {%- if semantic_model.name == model_name -%}
      {%- set ns.found_model = semantic_model -%}
      {%- break -%}
    {%- endif -%}
  {%- endfor -%}
  
  {{ return(ns.found_model) }}

{% endmacro %} 