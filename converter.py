#!/usr/bin/env python3
"""
Command-line interface for dbt Semantic Model to Snowflake Semantic View converter.
"""

import click
import sys
from pathlib import Path
from dbt_to_snowflake_converter import DBTToSnowflakeConverter


@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path), required=False)
@click.option('--overwrite', '-o', is_flag=True, help='Overwrite output file if it exists')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(input_file: Path, output_file: Path, overwrite: bool, verbose: bool):
    """
    Convert dbt semantic model YAML to Snowflake semantic view SQL.
    
    INPUT_FILE: Path to the dbt semantic model YAML file
    
    OUTPUT_FILE: Path for the generated SQL file (optional, prints to stdout if not provided)
    """
    try:
        # Initialize converter
        converter = DBTToSnowflakeConverter()
        
        if verbose:
            click.echo(f"Reading input file: {input_file}")
        
        # Convert the file
        sql_output = converter.convert_file(str(input_file))
        
        if verbose:
            click.echo("Conversion completed successfully!")
        
        # Output handling
        if output_file:
            # Check if output file exists
            if output_file.exists() and not overwrite:
                click.echo(f"Error: Output file '{output_file}' already exists. Use --overwrite to replace it.", err=True)
                sys.exit(1)
            
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(output_file, 'w') as f:
                f.write(sql_output)
            
            if verbose:
                click.echo(f"SQL written to: {output_file}")
            else:
                click.echo(f"Generated: {output_file}")
        else:
            # Print to stdout
            click.echo(sql_output)
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
def validate(input_file: Path):
    """
    Validate a dbt semantic model YAML file.
    """
    try:
        converter = DBTToSnowflakeConverter()
        
        # Attempt to parse and convert
        sql_output = converter.convert_file(str(input_file))
        
        click.echo(f"✓ Valid dbt semantic model: {input_file}")
        click.echo(f"✓ Would generate {len(sql_output.splitlines())} lines of SQL")
        
    except Exception as e:
        click.echo(f"✗ Invalid dbt semantic model: {input_file}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@click.group()
def cli():
    """dbt Semantic Model to Snowflake Semantic View Converter"""
    pass


cli.add_command(main, name='convert')
cli.add_command(validate)


if __name__ == '__main__':
    cli() 