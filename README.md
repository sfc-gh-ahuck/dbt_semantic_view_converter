# dbt Semantic View Converter

A dbt package that provides a custom materialization for creating Snowflake semantic views directly from dbt semantic model configurations.

## Overview

This dbt package bridges the gap between dbt's Semantic Layer and Snowflake's native semantic views, allowing you to:
- Transform dbt semantic model definitions into Snowflake semantic views using native dbt workflows
- Maintain consistent business logic across your semantic layer
- Leverage dbt's dependency management, testing, and documentation features
- Use familiar dbt materialization patterns for semantic views

## 🚀 Quick Start

### Installation

Add this package to your dbt project's `packages.yml`:

```yaml
packages:
  - git: "https://github.com/sfc-gh-ahuck/dbt_semantic_view_converter.git"
    revision: main
```

Then run:
```bash
dbt deps
```

### Usage

#### 1. Define Semantic Models

Create semantic models in your `schema.yml`:

```yaml
semantic_models:
  - name: orders
    description: "Order fact table"
    model: ref('dim_orders')
    entities:
      - name: order_id
        type: primary
      - name: customer_id
        type: foreign
    dimensions:
      - name: order_date
        type: time
        type_params:
          time_granularity: day
      - name: order_status
        type: categorical
    measures:
      - name: order_total
        agg: sum
      - name: order_count
        expr: 1
        agg: sum
```

#### 2. Create Semantic View Models

Create a model file using the `semantic_view` materialization:

```sql
-- models/semantic_views/orders_semantic_view.sql
{{ config(
    materialized='semantic_view',
    schema='semantic_layer'
) }}

SELECT 1 as placeholder
```

#### 3. Run dbt

```bash
dbt run --models orders_semantic_view
```

This creates a Snowflake semantic view based on your semantic model definition!

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

### Model-Level Configuration

```sql
{{ config(
    materialized='semantic_view',
    schema='my_semantic_layer',
    database='analytics',
    tags=['semantic', 'daily']
) }}
```

## 📖 Example Output

The package generates Snowflake `CREATE SEMANTIC VIEW` statements like:

```sql
CREATE OR REPLACE SEMANTIC VIEW analytics.semantic_layer.orders
  COMMENT = 'Order fact table'
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
    orders.order_date AS DATE_TRUNC('DAY', order_date),
    orders.order_status AS order_status
  )
  METRICS (
    orders.total_order_total AS SUM(order_total),
    orders.total_count AS COUNT(*)
  )
  COPY GRANTS;
```

## 🧪 Testing

Test the package with the included example models:

```bash
# Run example semantic views
dbt run --models semantic_views

# Check generated objects in Snowflake
SHOW SEMANTIC VIEWS;
```

## 📁 Project Structure

```
├── dbt_project.yml              # Package configuration
├── macros/
│   ├── materializations/
│   │   └── semantic_view.sql    # Custom materialization
│   ├── helpers/                 # Helper macros for SQL generation
│   └── *.sql                    # Core conversion logic
├── models/
│   └── semantic_views/          # Example models
├── docs/
│   └── usage_guide.md          # Detailed documentation
└── README.md
```

## 🔧 Advanced Usage

### Multiple Semantic Models

Define multiple semantic models and create corresponding view files:

```yaml
# schema.yml
semantic_models:
  - name: orders_semantic_view
    # ... configuration
  - name: customers_semantic_view  
    # ... configuration
```

```sql
-- models/semantic_views/orders_semantic_view.sql
{{ config(materialized='semantic_view') }}
SELECT 1 as placeholder

-- models/semantic_views/customers_semantic_view.sql
{{ config(materialized='semantic_view') }}
SELECT 1 as placeholder
```

### Custom Schema and Database

```sql
{{ config(
    materialized='semantic_view',
    schema='custom_semantic_layer',
    database='custom_analytics_db'
) }}
```

## 📚 Documentation

For detailed usage instructions, see [docs/usage_guide.md](docs/usage_guide.md).

## ⚠️ Requirements

- dbt >= 1.0.0
- Snowflake adapter
- Semantic models defined in your dbt project

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Transform your dbt semantic models into Snowflake semantic views with native dbt workflows! 🚀** 