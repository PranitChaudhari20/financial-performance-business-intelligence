-- =============================================================================
-- analysis_queries.sql  -  the financial questions, answered in SQL
-- Author: Pranit Ajay Chaudhari
--
-- Every figure produced here is cross-checked against the Python output by
-- python/06_verify.py. Ratios are always recomputed from summed amounts, never
-- averaged from row-level ratios, because the average of a ratio is not the
-- ratio of the sums.
-- =============================================================================
USE financial_performance;

-- QUERY 01 | Business KPIs | What is the overall financial picture?
SELECT COUNT(*)                                                  AS order_lines,
       COUNT(DISTINCT order_id)                                  AS orders,
       SUM(quantity)                                             AS units_sold,
       COUNT(DISTINCT product_id)                                AS distinct_products,
       COUNT(DISTINCT customer_id)                               AS distinct_customers,
       ROUND(SUM(gross_sales), 2)                                AS gross_sales,
       ROUND(SUM(discount_value), 2)                             AS discount_given,
       ROUND(SUM(discount_value) / SUM(gross_sales) * 100, 2)    AS discount_rate_pct,
       ROUND(SUM(revenue), 2)                                    AS net_revenue,
       ROUND(SUM(implied_cost), 2)                               AS implied_cost,
       ROUND(SUM(profit), 2)                                     AS profit,
       ROUND(SUM(profit) / SUM(revenue) * 100, 2)                AS net_margin_pct,
       ROUND(SUM(implied_cost) / SUM(revenue) * 100, 2)          AS cost_to_revenue_pct,
       ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2)         AS avg_order_value,
       ROUND(SUM(profit) / COUNT(DISTINCT order_id), 2)          AS profit_per_order,
       SUM(is_loss_making)                                       AS loss_making_lines,
       ROUND(SUM(is_loss_making) / COUNT(*) * 100, 2)            AS loss_making_lines_pct
FROM fact_order_lines;

-- QUERY 02 | Yearly performance and growth | How has the business moved year to year?
WITH yearly AS (
    SELECT d.year,
           COUNT(DISTINCT f.order_id) AS orders,
           SUM(f.revenue)             AS revenue,
           SUM(f.implied_cost)        AS implied_cost,
           SUM(f.profit)              AS profit
    FROM fact_order_lines f
    JOIN dim_date d ON d.date_key = f.order_date
    GROUP BY d.year
)
SELECT year, orders,
       ROUND(revenue, 2)                                              AS revenue,
       ROUND(implied_cost, 2)                                         AS implied_cost,
       ROUND(profit, 2)                                               AS profit,
       ROUND(profit / revenue * 100, 2)                               AS margin_pct,
       ROUND(implied_cost / revenue * 100, 2)                         AS cost_to_revenue_pct,
       ROUND((revenue / LAG(revenue) OVER (ORDER BY year) - 1) * 100, 2) AS revenue_growth_pct,
       ROUND((profit  / LAG(profit)  OVER (ORDER BY year) - 1) * 100, 2) AS profit_growth_pct,
       ROUND(revenue / orders, 2)                                     AS avg_order_value
FROM yearly
ORDER BY year;

-- QUERY 03 | Quarterly performance | The same picture at quarter grain
SELECT d.year_quarter,
       COUNT(DISTINCT f.order_id)                       AS orders,
       ROUND(SUM(f.revenue), 2)                         AS revenue,
       ROUND(SUM(f.profit), 2)                          AS profit,
       ROUND(SUM(f.profit) / SUM(f.revenue) * 100, 2)   AS margin_pct
FROM fact_order_lines f
JOIN dim_date d ON d.date_key = f.order_date
GROUP BY d.year_quarter
ORDER BY d.year_quarter;

-- QUERY 04 | Monthly trend | Revenue, margin and a three-month moving average
WITH monthly AS (
    SELECT d.month_key, COUNT(DISTINCT f.order_id) AS orders,
           SUM(f.revenue) AS revenue, SUM(f.profit) AS profit
    FROM fact_order_lines f
    JOIN dim_date d ON d.date_key = f.order_date
    GROUP BY d.month_key
)
SELECT month_key, orders,
       ROUND(revenue, 2)                            AS revenue,
       ROUND(profit, 2)                             AS profit,
       ROUND(profit / revenue * 100, 2)             AS margin_pct,
       ROUND((revenue / LAG(revenue) OVER (ORDER BY month_key) - 1) * 100, 2) AS revenue_growth_pct,
       ROUND(AVG(revenue) OVER (ORDER BY month_key ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2)
                                                    AS revenue_3mth_avg
FROM monthly
ORDER BY month_key;

-- QUERY 05 | Seasonality | Which months beat their own year's average, every year?
WITH m AS (
    SELECT d.year, d.month_num, SUM(f.revenue) AS revenue
    FROM fact_order_lines f
    JOIN dim_date d ON d.date_key = f.order_date
    GROUP BY d.year, d.month_num
), indexed AS (
    SELECT year, month_num, revenue,
           revenue / AVG(revenue) OVER (PARTITION BY year) * 100 AS idx
    FROM m
)
SELECT month_num,
       ROUND(AVG(idx), 1)                                   AS mean_index,
       ROUND(MIN(idx), 1)                                   AS min_index,
       SUM(CASE WHEN idx > 100 THEN 1 ELSE 0 END)           AS years_above_average,
       COUNT(*)                                             AS years_observed
FROM indexed
GROUP BY month_num
ORDER BY month_num;

-- QUERY 06 | Category performance | Where does revenue come from, and where does profit?
SELECT p.category,
       COUNT(DISTINCT f.order_id)                                      AS orders,
       SUM(f.quantity)                                                 AS units,
       ROUND(SUM(f.revenue), 2)                                        AS revenue,
       ROUND(SUM(f.revenue) / SUM(SUM(f.revenue)) OVER () * 100, 2)    AS revenue_share_pct,
       ROUND(SUM(f.implied_cost), 2)                                   AS implied_cost,
       ROUND(SUM(f.profit), 2)                                         AS profit,
       ROUND(SUM(f.profit) / SUM(SUM(f.profit)) OVER () * 100, 2)      AS profit_share_pct,
       ROUND(SUM(f.profit) / SUM(f.revenue) * 100, 2)                  AS margin_pct,
       ROUND(SUM(f.discount_value) / SUM(f.gross_sales) * 100, 2)      AS discount_rate_pct,
       ROUND(SUM(f.is_loss_making) / COUNT(*) * 100, 2)                AS loss_line_share_pct
FROM fact_order_lines f
JOIN dim_product p ON p.product_id = f.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- QUERY 07 | Sub-category performance | Which lines earn and which lose?
SELECT p.category, p.sub_category,
       ROUND(SUM(f.revenue), 2)                                        AS revenue,
       ROUND(SUM(f.revenue) / SUM(SUM(f.revenue)) OVER () * 100, 2)    AS revenue_share_pct,
       ROUND(SUM(f.implied_cost), 2)                                   AS implied_cost,
       ROUND(SUM(f.profit), 2)                                         AS profit,
       ROUND(SUM(f.profit) / SUM(f.revenue) * 100, 2)                  AS margin_pct,
       ROUND(SUM(f.discount_value) / SUM(f.gross_sales) * 100, 2)      AS discount_rate_pct,
       ROUND(SUM(f.is_loss_making) / COUNT(*) * 100, 2)                AS loss_line_share_pct
FROM fact_order_lines f
JOIN dim_product p ON p.product_id = f.product_id
GROUP BY p.category, p.sub_category
ORDER BY revenue DESC;

-- QUERY 08 | Regional performance | Which regions carry the business?
SELECT g.region,
       COUNT(DISTINCT f.order_id)                                      AS orders,
       ROUND(SUM(f.revenue), 2)                                        AS revenue,
       ROUND(SUM(f.revenue) / SUM(SUM(f.revenue)) OVER () * 100, 2)    AS revenue_share_pct,
       ROUND(SUM(f.implied_cost), 2)                                   AS implied_cost,
       ROUND(SUM(f.profit), 2)                                         AS profit,
       ROUND(SUM(f.profit) / SUM(SUM(f.profit)) OVER () * 100, 2)      AS profit_share_pct,
       ROUND(SUM(f.profit) / SUM(f.revenue) * 100, 2)                  AS margin_pct,
       ROUND(SUM(f.discount_value) / SUM(f.gross_sales) * 100, 2)      AS discount_rate_pct,
       ROUND(SUM(f.revenue) / COUNT(DISTINCT f.order_id), 2)           AS avg_order_value
FROM fact_order_lines f
JOIN dim_geography g ON g.geo_id = f.geo_id
GROUP BY g.region
ORDER BY revenue DESC;

-- QUERY 09 | States that lose money | Where is the business paying to trade?
SELECT g.region, g.state,
       ROUND(SUM(f.revenue), 2)                                   AS revenue,
       ROUND(SUM(f.profit), 2)                                    AS profit,
       ROUND(SUM(f.profit) / SUM(f.revenue) * 100, 2)             AS margin_pct,
       ROUND(SUM(f.discount_value) / SUM(f.gross_sales) * 100, 2) AS discount_rate_pct
FROM fact_order_lines f
JOIN dim_geography g ON g.geo_id = f.geo_id
GROUP BY g.region, g.state
HAVING SUM(f.profit) < 0
ORDER BY profit;

-- QUERY 10 | Discount band versus margin | What does discounting cost?
SELECT f.discount_band,
       COUNT(*)                                                   AS line_count,
       ROUND(SUM(f.gross_sales), 2)                               AS gross_sales,
       ROUND(SUM(f.discount_value), 2)                            AS discount_value,
       ROUND(SUM(f.revenue), 2)                                   AS revenue,
       ROUND(SUM(f.implied_cost), 2)                              AS implied_cost,
       ROUND(SUM(f.profit), 2)                                    AS profit,
       ROUND(SUM(f.profit) / SUM(f.revenue) * 100, 2)             AS margin_pct,
       ROUND(SUM(f.is_loss_making) / COUNT(*) * 100, 2)           AS loss_line_share_pct
FROM fact_order_lines f
GROUP BY f.discount_band
ORDER BY MIN(f.discount);

-- QUERY 11 | Exact discount rate versus margin | Where is the break-even point?
SELECT f.discount,
       COUNT(*)                                          AS line_count,
       ROUND(SUM(f.revenue), 2)                          AS revenue,
       ROUND(SUM(f.profit), 2)                           AS profit,
       ROUND(SUM(f.profit) / SUM(f.revenue) * 100, 2)    AS margin_pct,
       ROUND(SUM(f.is_loss_making) / COUNT(*) * 100, 2)  AS loss_line_share_pct
FROM fact_order_lines f
GROUP BY f.discount
ORDER BY f.discount;

-- QUERY 12 | Cost structure | From list value down to profit
SELECT ROUND(SUM(gross_sales), 2)                                AS gross_sales,
       ROUND(SUM(discount_value), 2)                             AS discount_given,
       ROUND(SUM(revenue), 2)                                    AS net_revenue,
       ROUND(SUM(implied_cost), 2)                               AS implied_cost_of_sales,
       ROUND(SUM(profit), 2)                                     AS profit,
       ROUND(SUM(discount_value) / SUM(gross_sales) * 100, 2)    AS discount_pct_of_gross,
       ROUND(SUM(implied_cost) / SUM(gross_sales) * 100, 2)      AS cost_pct_of_gross,
       ROUND(SUM(profit) / SUM(gross_sales) * 100, 2)            AS profit_pct_of_gross
FROM fact_order_lines;

-- QUERY 13 | Cost trend | Is cost growing faster than revenue?
WITH yearly AS (
    SELECT d.year, SUM(f.revenue) AS revenue, SUM(f.implied_cost) AS implied_cost,
           SUM(f.profit) AS profit
    FROM fact_order_lines f
    JOIN dim_date d ON d.date_key = f.order_date
    GROUP BY d.year
)
SELECT year,
       ROUND(revenue, 2)                                                        AS revenue,
       ROUND(implied_cost, 2)                                                   AS implied_cost,
       ROUND(implied_cost / revenue * 100, 2)                                   AS cost_to_revenue_pct,
       ROUND((implied_cost / LAG(implied_cost) OVER (ORDER BY year) - 1) * 100, 2) AS cost_growth_pct,
       ROUND((revenue / LAG(revenue) OVER (ORDER BY year) - 1) * 100, 2)        AS revenue_growth_pct
FROM yearly
ORDER BY year;

-- QUERY 14 | Revenue concentration | How much of the catalogue carries the revenue?
WITH per_product AS (
    SELECT product_id, SUM(revenue) AS revenue, SUM(profit) AS profit
    FROM fact_order_lines GROUP BY product_id
), ranked AS (
    SELECT product_id, revenue, profit,
           ROW_NUMBER() OVER (ORDER BY revenue DESC)                              AS rn,
           SUM(revenue) OVER (ORDER BY revenue DESC
                              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)   AS cum_revenue,
           SUM(revenue) OVER ()                                                   AS total_revenue,
           COUNT(*)    OVER ()                                                    AS product_count
    FROM per_product
)
SELECT product_count                                                        AS products,
       MIN(CASE WHEN cum_revenue >= total_revenue * 0.5 THEN rn END)        AS products_for_half_revenue,
       ROUND(MAX(CASE WHEN rn <= CEIL(product_count * 0.10) THEN cum_revenue END)
             / MAX(total_revenue) * 100, 2)                                 AS top_10pct_revenue_share,
       ROUND(MAX(CASE WHEN rn <= CEIL(product_count * 0.20) THEN cum_revenue END)
             / MAX(total_revenue) * 100, 2)                                 AS top_20pct_revenue_share,
       SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END)                          AS loss_making_products,
       ROUND(SUM(CASE WHEN profit < 0 THEN profit ELSE 0 END), 2)           AS loss_from_those_products
FROM ranked
GROUP BY product_count;

-- QUERY 15 | Segment performance | Which customer segment is most profitable to serve?
SELECT f.segment,
       COUNT(DISTINCT f.order_id)                                   AS orders,
       ROUND(SUM(f.revenue), 2)                                     AS revenue,
       ROUND(SUM(f.revenue) / SUM(SUM(f.revenue)) OVER () * 100, 2) AS revenue_share_pct,
       ROUND(SUM(f.profit), 2)                                      AS profit,
       ROUND(SUM(f.profit) / SUM(f.revenue) * 100, 2)               AS margin_pct,
       ROUND(SUM(f.revenue) / COUNT(DISTINCT f.order_id), 2)        AS avg_order_value
FROM fact_order_lines f
GROUP BY f.segment
ORDER BY revenue DESC;

-- QUERY 16 | Worst products by profit | What should management look at first?
SELECT f.product_id, p.product_name, p.category, p.sub_category,
       ROUND(SUM(f.revenue), 2)                        AS revenue,
       ROUND(SUM(f.profit), 2)                         AS profit,
       ROUND(SUM(f.profit) / SUM(f.revenue) * 100, 2)  AS margin_pct,
       SUM(f.quantity)                                 AS units
FROM fact_order_lines f
JOIN dim_product p ON p.product_id = f.product_id
GROUP BY f.product_id, p.product_name, p.category, p.sub_category
ORDER BY profit ASC
LIMIT 20;
