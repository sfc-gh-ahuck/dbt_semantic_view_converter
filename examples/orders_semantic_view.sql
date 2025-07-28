CREATE SEMANTIC VIEW orders
  COMMENT = 'Order fact table containing transaction data at the order level'
  TABLES (
    orders AS dim_orders
      PRIMARY KEY (order_id)
  )
  RELATIONSHIPS (
    to_customer_id AS
      semantic_model (customer_id) REFERENCES customer,
    to_location_id AS
      semantic_model (store_location_id) REFERENCES location
  )
  FACTS (
    orders.order_total AS order_total
      COMMENT 'Total value of the order including taxes',
    orders.avg_order_value AS order_total
      COMMENT 'Average order value'
  )
  DIMENSIONS (
    orders.order_date AS date_trunc('day', order_date)
      COMMENT 'Date when the order was placed',
    orders.order_status AS order_status
      COMMENT 'Current status of the order',
    orders.is_large_order AS case when order_total > 100 then true else false end
      COMMENT 'Flag indicating if order value exceeds $100'
  )
  METRICS (
    orders.order_total AS SUM(order_total)
      COMMENT 'Total value of the order including taxes',
    orders.total_count AS SUM(1)
      COMMENT 'Count of individual orders',
    orders.avg_avg_order_value AS AVG(order_total)
      COMMENT 'Average order value',
    orders.unique_customers AS COUNT(DISTINCT customer_id)
      COMMENT 'Count of unique customers'
  );