{{ config(
    materialized='semantic_view',
    schema='semantic_layer'
) }}

-- This model creates a Snowflake semantic view from the customers semantic model
-- The semantic model configuration should be defined in the schema.yml file

SELECT 1 as placeholder 