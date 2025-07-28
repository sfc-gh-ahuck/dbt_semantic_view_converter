#!/usr/bin/env python3
"""
Example usage of the dbt Semantic Model to Snowflake Semantic View converter.
"""

from dbt_to_snowflake_converter import DBTToSnowflakeConverter

def main():
    """Demonstrate various ways to use the converter."""
    
    # Initialize the converter
    converter = DBTToSnowflakeConverter()
    
    print("=== dbt Semantic Model to Snowflake Semantic View Converter ===\n")
    
    # Example 1: Convert from file
    print("1. Converting orders semantic model...")
    try:
        sql_output = converter.convert_file('examples/orders_semantic_model.yml')
        print("✓ Successfully converted orders semantic model")
        print(f"✓ Generated {len(sql_output.splitlines())} lines of SQL\n")
    except Exception as e:
        print(f"✗ Error converting orders: {e}\n")
    
    # Example 2: Convert from YAML content directly
    print("2. Converting from YAML content...")
    
    yaml_content = {
        'semantic_models': [
            {
                'name': 'simple_model',
                'description': 'A simple example semantic model',
                'model': 'ref(\'my_table\')',
                'entities': [
                    {'name': 'id', 'type': 'primary'},
                    {'name': 'user_id', 'type': 'foreign'}
                ],
                'dimensions': [
                    {
                        'name': 'created_date',
                        'type': 'time',
                        'type_params': {'time_granularity': 'day'},
                        'description': 'Creation date'
                    },
                    {
                        'name': 'status',
                        'type': 'categorical',
                        'description': 'Record status'
                    }
                ],
                'measures': [
                    {
                        'name': 'amount',
                        'agg': 'sum',
                        'description': 'Total amount'
                    },
                    {
                        'name': 'record_count',
                        'expr': '1',
                        'agg': 'sum',
                        'description': 'Count of records'
                    }
                ]
            }
        ]
    }
    
    try:
        sql_output = converter.convert_yaml_content(yaml_content)
        print("✓ Successfully converted YAML content")
        print("Generated SQL:")
        print("-" * 50)
        print(sql_output)
        print("-" * 50)
    except Exception as e:
        print(f"✗ Error converting YAML content: {e}")
    
    print("\n=== Conversion Complete ===")
    print("Check the examples/ directory for sample input and output files.")

if __name__ == '__main__':
    main() 