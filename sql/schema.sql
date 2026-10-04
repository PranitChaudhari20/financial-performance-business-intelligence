-- =============================================================================
-- schema.sql  -  star schema for Financial Performance & BI Analytics
-- Author: Pranit Ajay Chaudhari
-- Engine: MySQL 8 / MariaDB 10.5+
--
-- One fact table of order lines surrounded by product, geography and date
-- dimensions. The financial measures live on the fact table because they are
-- additive at the order-line grain; the ratios (margin, cost-to-revenue,
-- discount rate) are deliberately NOT stored, because a stored ratio cannot be
-- aggregated correctly - every query recomputes them from the sums.
-- =============================================================================

DROP DATABASE IF EXISTS financial_performance;
CREATE DATABASE financial_performance
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE financial_performance;

CREATE TABLE dim_product (
    product_id    VARCHAR(20)  NOT NULL,
    category      VARCHAR(40)  NOT NULL,
    sub_category  VARCHAR(40)  NOT NULL,
    product_name  VARCHAR(220) NOT NULL,
    PRIMARY KEY (product_id),
    KEY ix_prod_cat (category),
    KEY ix_prod_sub (sub_category)
) ENGINE=InnoDB;

CREATE TABLE dim_geography (
    geo_id       INT          NOT NULL AUTO_INCREMENT,
    region       VARCHAR(20)  NOT NULL,
    state        VARCHAR(40)  NOT NULL,
    city         VARCHAR(60)  NOT NULL,
    postal_code  VARCHAR(12)  NULL,
    PRIMARY KEY (geo_id),
    UNIQUE KEY ux_geo (region, state, city, postal_code),
    KEY ix_geo_region (region),
    KEY ix_geo_state  (state)
) ENGINE=InnoDB;

CREATE TABLE dim_date (
    date_key    DATE    NOT NULL,
    year        INT     NOT NULL,
    quarter     INT     NOT NULL,
    year_quarter CHAR(7) NOT NULL,
    month_num   INT     NOT NULL,
    month_name  CHAR(3) NOT NULL,
    month_key   CHAR(7) NOT NULL,     -- 'year_month' is a reserved word in MariaDB
    PRIMARY KEY (date_key),
    KEY ix_date_year  (year),
    KEY ix_date_month (month_key)
) ENGINE=InnoDB;

CREATE TABLE fact_order_lines (
    row_id          INT            NOT NULL,
    order_id        VARCHAR(20)    NOT NULL,
    order_date      DATE           NOT NULL,
    ship_date       DATE           NOT NULL,
    ship_mode       VARCHAR(20)    NOT NULL,
    customer_id     VARCHAR(20)    NOT NULL,
    segment         VARCHAR(20)    NOT NULL,
    product_id      VARCHAR(20)    NOT NULL,
    geo_id          INT            NOT NULL,
    quantity        INT            NOT NULL,
    discount        DECIMAL(5,3)   NOT NULL,
    discount_band   VARCHAR(12)    NOT NULL,
    gross_sales     DECIMAL(12,4)  NOT NULL,   -- Sales / (1 - Discount)
    discount_value  DECIMAL(12,4)  NOT NULL,   -- gross_sales - revenue
    revenue         DECIMAL(12,4)  NOT NULL,   -- the dataset's Sales, net of discount
    implied_cost    DECIMAL(12,4)  NOT NULL,   -- revenue - profit (a RESIDUAL, not a reported cost)
    profit          DECIMAL(12,4)  NOT NULL,
    is_loss_making  TINYINT(1)     NOT NULL,
    PRIMARY KEY (row_id),
    KEY ix_f_order  (order_id),
    KEY ix_f_date   (order_date),
    KEY ix_f_prod   (product_id),
    KEY ix_f_geo    (geo_id),
    KEY ix_f_disc   (discount_band),
    KEY ix_f_loss   (is_loss_making),
    CONSTRAINT fk_f_prod FOREIGN KEY (product_id) REFERENCES dim_product (product_id),
    CONSTRAINT fk_f_geo  FOREIGN KEY (geo_id)     REFERENCES dim_geography (geo_id),
    CONSTRAINT fk_f_date FOREIGN KEY (order_date) REFERENCES dim_date (date_key)
) ENGINE=InnoDB;
