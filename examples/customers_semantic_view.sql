CREATE SEMANTIC VIEW customers
  COMMENT = 'Customer dimension table with demographics and segmentation data'
  TABLES (
    customers AS dim_customers
      PRIMARY KEY (customer_id)
  )
  FACTS (
    customers.customer_lifetime_value AS total_spent
      COMMENT 'Total lifetime value of customer'
  )
  DIMENSIONS (
    customers.customer_name AS full_name
      COMMENT 'Customer's full name',
    customers.customer_segment AS customer_segment
      COMMENT 'Customer segment classification',
    customers.registration_date AS DATE_TRUNC('DAY', registration_date)
      COMMENT 'Date when customer registered',
    customers.country AS country
      COMMENT 'Customer's country',
    customers.age_group AS (
        case
          WHEN age < 25 THEN 'Young'
          WHEN age between 25 and 50 THEN 'Middle'
          ELSE 'Senior'
          END
    )
      COMMENT 'Customer age group classification'
  )
  METRICS (
    customers.customer_lifetime_value AS SUM(total_spent)
      COMMENT 'Total lifetime value of customer',
    customers.total_count AS SUM(1)
      COMMENT 'Total number of customers'
  );