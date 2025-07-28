# dbt Semantic Model to Snowflake Semantic View Converter

A comprehensive solution for converting dbt semantic models into Snowflake semantic views, available as both a **Python standalone tool** and a **dbt package with custom materialization**.

## Overview

This project bridges the gap between dbt's Semantic Layer and Snowflake's native semantic views, allowing you to:
- Transform dbt semantic model definitions into Snowflake-compatible SQL
- Maintain consistent business logic across different semantic layer implementations
- Migrate from dbt semantic models to Snowflake semantic views
- Use native dbt workflows with custom materialization

## 🚀 Quick Start

### Option 1: dbt Package (Recommended)

Add this package to your dbt project's `packages.yml`:

```yaml
packages:
  - git: "https://github.com/your-org/dbt-semantic-model-to-snowflake-semantic-view-converter.git"
    revision: main
```

Then run:
```bash
dbt deps
```

### Option 2: Python Tool

```bash
pip install -r requirements.txt
python converter.py input.yml output.sql
```

## 📦 Using the dbt Package

### 1. Define Semantic Models

Create semantic models in your `schema.yml`:

```yaml
semantic_models:
  - name: orders
    description: "Order fact table"
    model: ref('dim_orders')
    entities:
      - name: order_id
        type: primary
    dimensions:
      - name: order_date
        type: time
        type_params:
          time_granularity: day
    measures:
      - name: order_total
        agg: sum
```

### 2. Create Semantic View Models

Create a model file using the `semantic_view` materialization:

```sql
-- models/semantic_views/orders_semantic_view.sql
{{ config(
    materialized='semantic_view',
    schema='semantic_layer'
) }}

SELECT 1 as placeholder
```

### 3. Run dbt

```bash
dbt run --models orders_semantic_view
```

This will create a Snowflake semantic view based on your semantic model definition!

## ⚙️ Configuration

### Package Variables

Configure the package in your `dbt_project.yml`:

```yaml
vars:
  dbt_semantic_view_converter:
    semantic_views_database: "{{ target.database }}"
    semantic_views_schema: "semantic_layer"
    copy_grants: true
```

## 🐍 Using the Python Tool

### Command Line

```bash
# Convert YAML to SQL
python converter.py convert input.yml output.sql

# Validate a semantic model
python converter.py validate input.yml

# Print to stdout
python converter.py convert input.yml
```

### Python API

```python
from dbt_to_snowflake_converter import DBTToSnowflakeConverter

converter = DBTToSnowflakeConverter()
sql_output = converter.convert_file('semantic_model.yml')
print(sql_output)
```

## 📖 Example

### Input (dbt semantic model YAML):
```yaml
semantic_models:
  - name: orders
    model: ref('dim_orders')
    entities:
      - name: order_id
        type: primary
      - name: customer_id
        type: foreign
    dimensions:
      - name: order_date
        type: time
        time_granularity: day
    measures:
      - name: order_total
        agg: sum
```

### Output (Snowflake semantic view SQL):
```sql
CREATE SEMANTIC VIEW orders
  TABLES (
    orders AS dim_orders
      PRIMARY KEY (order_id)
  )
  RELATIONSHIPS (
    to_customer_id AS
      semantic_model (customer_id) REFERENCES customer
  )
  FACTS (
    orders.order_total AS order_total
  )
  DIMENSIONS (
    orders.order_date AS DATE_TRUNC('DAY', order_date)
  )
  METRICS (
    orders.total_order_total AS SUM(order_total)
  );
```

## 🧪 Testing

Test the dbt package with sample models:

```bash
# Run example semantic views
dbt run --models semantic_views

# Check generated objects in Snowflake
SHOW SEMANTIC VIEWS;
```

## 📁 Project Structure

```
├── dbt_project.yml              # dbt package configuration
├── macros/
│   ├── materializations/
│   │   └── semantic_view.sql    # Custom materialization
│   ├── helpers/                 # Helper macros
│   └── get_semantic_model_config.sql
├── models/
│   └── semantic_views/          # Example models
├── examples/                    # Python tool examples
├── dbt_to_snowflake_converter.py # Python converter
├── converter.py                 # CLI tool
└── README.md
```

## 🔧 Advanced Usage

### Custom Schema Placement

```sql
{{ config(
    materialized='semantic_view',
    schema='my_semantic_layer',
    database='analytics'
) }}
```

### Multiple Semantic Models

You can define multiple semantic models in a single `schema.yml` and create corresponding model files for each.

## ⚠️ Limitations

- **dbt Package**: Requires Snowflake adapter, dbt >= 1.0.0
- **Python Tool**: Foreign key relationships require manual target table definition
- Complex expressions may need manual review
- Time dimension granularity mapping is approximate

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Choose your workflow:**
- 🔄 **dbt Package**: Integrated with dbt, automatic builds, native workflows
- ⚡ **Python Tool**: Standalone conversion, custom pipelines, CLI automation 