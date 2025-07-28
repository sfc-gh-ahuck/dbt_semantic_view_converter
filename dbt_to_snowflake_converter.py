import yaml
import re
from typing import Dict, List, Any, Optional
from jinja2 import Template


class DBTToSnowflakeConverter:
    """
    Converts dbt semantic models (YAML) to Snowflake semantic views (SQL).
    """
    
    def __init__(self):
        self.aggregation_mapping = {
            'sum': 'SUM',
            'avg': 'AVG', 
            'average': 'AVG',
            'count': 'COUNT',
            'count_distinct': 'COUNT',
            'min': 'MIN',
            'max': 'MAX',
            'median': 'MEDIAN',
            'percentile': 'PERCENTILE_CONT',
            'sum_boolean': 'SUM'
        }
        
        self.time_granularity_mapping = {
            'day': 'DAY',
            'week': 'WEEK', 
            'month': 'MONTH',
            'quarter': 'QUARTER',
            'year': 'YEAR',
            'hour': 'HOUR',
            'minute': 'MINUTE'
        }
    
    def convert_file(self, input_file: str) -> str:
        """
        Convert a dbt semantic model YAML file to Snowflake semantic view SQL.
        
        Args:
            input_file: Path to the input YAML file
            
        Returns:
            Generated SQL for Snowflake semantic view
        """
        with open(input_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return self.convert_yaml_content(data)
    
    def convert_yaml_content(self, data: Dict[str, Any]) -> str:
        """
        Convert parsed YAML content to Snowflake semantic view SQL.
        
        Args:
            data: Parsed YAML data
            
        Returns:
            Generated SQL for Snowflake semantic view
        """
        if 'semantic_models' not in data:
            raise ValueError("No semantic_models found in YAML")
        
        semantic_models = data['semantic_models']
        if not semantic_models:
            raise ValueError("semantic_models list is empty")
        
        # Generate SQL for each semantic model
        sql_outputs = []
        for model in semantic_models:
            sql_output = self._convert_single_model(model)
            sql_outputs.append(sql_output)
        
        return '\n\n'.join(sql_outputs)
    
    def _convert_single_model(self, model: Dict[str, Any]) -> str:
        """
        Convert a single dbt semantic model to Snowflake semantic view SQL.
        
        Args:
            model: Single semantic model dictionary
            
        Returns:
            SQL for the semantic view
        """
        name = model.get('name')
        if not name:
            raise ValueError("Semantic model must have a name")
        
        description = model.get('description', '')
        model_ref = model.get('model', '')
        
        # Extract table name from model ref (e.g., "ref('table_name')" -> "table_name")
        table_name = self._extract_table_name(model_ref)
        
        # Process components
        tables_sql = self._generate_tables_section(name, table_name, model.get('entities', []))
        relationships_sql = self._generate_relationships_section(model.get('entities', []))
        facts_sql = self._generate_facts_section(name, model.get('measures', []))
        dimensions_sql = self._generate_dimensions_section(name, model.get('dimensions', []))
        metrics_sql = self._generate_metrics_section(name, model.get('measures', []))
        
        # Build the complete SQL
        template = Template("""CREATE SEMANTIC VIEW {{ name }}
{%- if description %}
  COMMENT = '{{ description | replace("'", "''") }}'
{%- endif %}
  TABLES (
{{ tables_sql | indent(4, True) }}
  )
{%- if relationships_sql %}
  RELATIONSHIPS (
{{ relationships_sql | indent(4, True) }}
  )
{%- endif %}
{%- if facts_sql %}
  FACTS (
{{ facts_sql | indent(4, True) }}
  )
{%- endif %}
{%- if dimensions_sql %}
  DIMENSIONS (
{{ dimensions_sql | indent(4, True) }}
  )
{%- endif %}
{%- if metrics_sql %}
  METRICS (
{{ metrics_sql | indent(4, True) }}
  )
{%- endif %};""")
        
        return template.render(
            name=name,
            description=description,
            tables_sql=tables_sql,
            relationships_sql=relationships_sql,
            facts_sql=facts_sql,
            dimensions_sql=dimensions_sql,
            metrics_sql=metrics_sql
        )
    
    def _extract_table_name(self, model_ref: str) -> str:
        """Extract table name from dbt model reference."""
        if not model_ref:
            return "unknown_table"
        
        # Handle ref() function
        if model_ref.startswith("ref("):
            match = re.search(r"ref\(['\"]([^'\"]+)['\"]", model_ref)
            if match:
                return match.group(1)
        
        # Return as-is if no ref() function
        return model_ref.strip("'\"")
    
    def _generate_tables_section(self, semantic_model_name: str, table_name: str, entities: List[Dict]) -> str:
        """Generate the TABLES section of the semantic view."""
        primary_key = None
        
        # Find primary entity
        for entity in entities:
            if entity.get('type') == 'primary':
                primary_key = entity.get('expr', entity.get('name'))
                break
        
        if not primary_key:
            # If no primary key found, use first entity or default
            if entities:
                primary_key = entities[0].get('expr', entities[0].get('name', 'id'))
            else:
                primary_key = 'id'
        
        table_alias = semantic_model_name
        
        return f"{table_alias} AS {table_name}\n  PRIMARY KEY ({primary_key})"
    
    def _generate_relationships_section(self, entities: List[Dict]) -> str:
        """Generate the RELATIONSHIPS section."""
        relationships = []
        
        for entity in entities:
            if entity.get('type') == 'foreign':
                entity_name = entity.get('name')
                expr = entity.get('expr', entity_name)
                
                # Create a relationship name and assume target table
                # Note: This is a limitation - we need to infer or require target table info
                relationship_name = f"to_{entity_name}"
                target_table = entity_name.replace('_id', '').replace('id', '') or 'unknown'
                
                relationships.append(
                    f"{relationship_name} AS\n"
                    f"  semantic_model ({expr}) REFERENCES {target_table}"
                )
        
        return ',\n'.join(relationships) if relationships else ""
    
    def _generate_facts_section(self, table_alias: str, measures: List[Dict]) -> str:
        """
        Generate the FACTS section for row-level data.
        In Snowflake semantic views, facts should be row-level attributes, not aggregated measures.
        We'll only include measures that represent row-level facts (not aggregations).
        """
        facts = []
        
        for measure in measures:
            name = measure.get('name')
            expr = measure.get('expr', name)
            description = measure.get('description', '')
            agg = measure.get('agg', 'sum')
            
            # Only include as facts if they represent row-level data
            # Skip measures that are clearly aggregations for the metrics section
            expr_str = str(expr)
            if expr_str != '1' and agg.lower() not in ['count', 'count_distinct'] and not expr_str.upper().startswith('COUNT'):
                fact_definition = f"{table_alias}.{name} AS {expr}"
                if description:
                    fact_definition += f"\n  COMMENT '{description}'"
                
                facts.append(fact_definition)
        
        return ',\n'.join(facts) if facts else ""
    
    def _generate_dimensions_section(self, table_alias: str, dimensions: List[Dict]) -> str:
        """Generate the DIMENSIONS section."""
        dims = []
        
        for dimension in dimensions:
            name = dimension.get('name')
            expr = dimension.get('expr', name)
            description = dimension.get('description', '')
            dim_type = dimension.get('type', 'categorical')
            
            # Handle time dimensions with granularity
            if dim_type == 'time':
                type_params = dimension.get('type_params', {})
                granularity = type_params.get('time_granularity', 'day')
                if expr == name and granularity:
                    # If no custom expression, add DATE_TRUNC for time dimensions
                    mapped_granularity = self.time_granularity_mapping.get(granularity, granularity.upper())
                    expr = f"DATE_TRUNC('{mapped_granularity}', {name})"
            
            # Format long expressions nicely
            if len(expr) > 60:
                expr_lines = self._wrap_long_expression(expr)
                dim_definition = f"{table_alias}.{name} AS (\n{expr_lines}\n)"
            else:
                dim_definition = f"{table_alias}.{name} AS {expr}"
            
            if description:
                dim_definition += f"\n  COMMENT '{description}'"
            
            dims.append(dim_definition)
        
        return ',\n'.join(dims) if dims else ""
    
    def _generate_metrics_section(self, table_alias: str, measures: List[Dict]) -> str:
        """Generate the METRICS section."""
        metrics = []
        
        for measure in measures:
            name = measure.get('name')
            agg = measure.get('agg', 'sum')
            expr = measure.get('expr', name)
            description = measure.get('description', '')
            
            # Map dbt aggregation to Snowflake
            snowflake_agg = self.aggregation_mapping.get(agg.lower(), agg.upper())
            
            # Handle special cases
            if agg.lower() == 'count_distinct':
                metric_expr = f"COUNT(DISTINCT {expr})"
            elif expr == '1' and agg.lower() in ['sum', 'count']:
                # Handle count metrics like dbt's "expr: 1, agg: sum"
                metric_expr = f"COUNT(*)"
            else:
                metric_expr = f"{snowflake_agg}({expr})"
            
            # Generate cleaner metric names
            metric_name = self._generate_metric_name(name, agg)
            metric_definition = f"{table_alias}.{metric_name} AS {metric_expr}"
            
            if description:
                metric_definition += f"\n  COMMENT '{description}'"
            
            metrics.append(metric_definition)
        
        return ',\n'.join(metrics) if metrics else ""
    
    def _generate_metric_name(self, measure_name: str, agg: str) -> str:
        """Generate a clean metric name based on measure name and aggregation."""
        agg_lower = agg.lower()
        
        # Common patterns for cleaner names
        if agg_lower == 'sum':
            if measure_name.endswith('_count') or measure_name == 'count':
                return 'total_count'
            elif measure_name.endswith('_total') or measure_name.endswith('_amount') or measure_name.endswith('_value'):
                return measure_name  # Already descriptive
            else:
                return f"total_{measure_name}"
        elif agg_lower == 'avg' or agg_lower == 'average':
            return f"avg_{measure_name}"
        elif agg_lower == 'count':
            return f"{measure_name}_count" if not measure_name.endswith('_count') else measure_name
        elif agg_lower == 'count_distinct':
            return f"unique_{measure_name}" if not measure_name.startswith('unique_') else measure_name
        elif agg_lower in ['min', 'max']:
            return f"{agg_lower}_{measure_name}"
        else:
            return f"{agg_lower}_{measure_name}"
    
    def _wrap_long_expression(self, expr: str) -> str:
        """Wrap long expressions for better readability."""
        # Simple wrapping for case statements and long expressions
        if 'case ' in expr.lower():
            # Format case statements nicely
            expr = re.sub(r'\s+when\s+', '\n      WHEN ', expr, flags=re.IGNORECASE)
            expr = re.sub(r'\s+then\s+', ' THEN ', expr, flags=re.IGNORECASE)
            expr = re.sub(r'\s+else\s+', '\n      ELSE ', expr, flags=re.IGNORECASE)
            expr = re.sub(r'\s+end\s*', '\n      END', expr, flags=re.IGNORECASE)
            return f"    {expr}"
        else:
            # Simple line wrapping for other long expressions
            return f"    {expr}" 