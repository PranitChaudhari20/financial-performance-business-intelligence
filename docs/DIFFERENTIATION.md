# How Project 4 differs from Projects 1, 2 and 3

*Author: Pranit Ajay Chaudhari*

This page was written after reading the actual files of all three earlier projects — their READMEs,
SQL query sets, result tables and limitations documents — not from memory of what they were
supposed to contain.

---

## The short version

**Projects 1, 2 and 3 all say, in their own documentation, that they cannot measure profitability.
Project 4 is the one that can.**

Project 1's README states:

> *"The dataset does not contain margins, demographics or campaign-response history, so
> profitability and campaign response cannot be directly measured."*

Project 3's limitations document states:

> *"Every recommendation here is framed in revenue and contact cost, never profit … the data
> contains no cost of goods."*
> *"No product-level cost, stock or margin, so category recommendations are about revenue mix only."*

Project 2 has no money in it at all — it analyses nutrition attributes of menu items, and its own
documentation records that no prices were ever collected.

**Searching all three projects for cost-of-sales analysis returns nothing**: zero files in any of
them mention cost of sales, COGS or an implied cost. Project 4 is built entirely on that axis.

---

## Against Project 1 — *Customer Segmentation & Marketing Analytics*

UCI Online Retail II: a UK gift-ware wholesaler, 770,612 clean order lines, 5,839 customers,
£16.53M, segmented with RFM into 11 segments across 4 tiers.

| | Project 1 | Project 4 |
|---|---|---|
| Unit of analysis | the **customer** | the **order line's financial contribution** |
| Central question | which customers matter and what do we send them? | where does the money go between list price and profit? |
| Core method | RFM segmentation, cohort retention, market-basket affinity | margin decomposition, cost-to-revenue, discount break-even, contribution analysis |
| Does the data have cost? | **No** — its README says profitability cannot be measured | **Yes** — per-line profit, from which cost is recoverable |
| Does the data have discount? | discount service codes were **removed in cleaning** | discount rate per line is a **primary variable** |
| Output | segment map and targeting actions | cost structure, loss-making lines, KPI set, management priorities |

Project 1's SQL asks: top 10 customers, purchase frequency distribution, at-risk high-value
customers, cohort retention, new versus returning, products bought together, champions versus lost.
**Project 4's SQL asks none of those.** It asks: cost structure, cost trend, discount band versus
margin, sub-category profitability, states that lose money, revenue concentration, break-even
discount rate.

## Against Project 2 — *Fast-Food Product & Nutrition Analytics*

713 menu items from McDonald's, Burger King and KFC, analysed on nutrition attributes.

| | Project 2 | Project 4 |
|---|---|---|
| Unit of analysis | a **menu item** | an **order line** |
| Does it contain money? | **No.** No prices were collected; the price template ships deliberately blank | Yes — 2.86M gross sales, 2.30M net revenue, 0.29M profit |
| Does it contain transactions? | No | 9,994 order lines across 5,009 orders |
| Does it contain time? | No | 48 continuous months |
| Core measures | calories, protein per 100 kcal, sodium density | revenue, discount, implied cost, profit, margin |
| Business question | how is each brand's menu positioned? | where is the business making and losing money? |

There is no overlap in data, unit of analysis, measures or conclusions. The only thing shared is the
toolchain, which is the point of a portfolio.

## Against Project 3 — *E-Commerce Growth & Acquisition Analytics*

Olist marketplace (96,470 orders) plus a marketing-campaign dataset (2,026 customers), kept
separate.

This is the closest of the three, because both projects analyse order data from a retailer. The
difference is what is measured.

| | Project 3 | Project 4 |
|---|---|---|
| Central question | where does **growth** come from, and should we spend on acquisition or retention? | where does **profit** come from, and what is destroying it? |
| Headline finding | 96.97% of customers never return; retention is worth $4.91 per customer | 18.72% of order lines are sold below cost; margin turns negative above a 20% discount |
| Unit of analysis | the **customer** and the customer's first order | the **order line** and its margin |
| Cost and profit | **absent from the data**, stated as a limitation | the core of the project |
| Discount | a *customer behaviour* variable — "deal-driven" customers in Part B | a *pricing* variable — the break-even discount rate |
| Time analysis | monthly new-versus-returning, cohort retention | monthly, quarterly and yearly revenue, cost and margin, with a tested seasonality pattern |
| Geography | acquisition economics by Brazilian state (freight, delivery) | profitability by US region and state (margin, discount rate, loss-making states) |
| Segmentation | RFM value tiers, campaign responsiveness, discount dependence | **none** — `Segment` appears only as a revenue and margin dimension |

### Query-by-query, measured rather than asserted

Of Project 4's 16 SQL queries, **none** has an equivalent in Project 3. Project 3's queries about
order frequency, customer value decomposition, value tiers, delivery speed versus repeat purchase,
review score versus repeat purchase, campaign performance and the targeting matrix have no
counterpart here, because this project never looks at a customer's behaviour over time.

Project 4's queries that exist nowhere else in the portfolio: **cost structure**, **cost trend**,
**discount band versus margin**, **exact discount rate versus margin**, **sub-category
profitability**, **states that lose money**, **revenue concentration by product**, **worst products
by profit**, **seasonality index**.

### Deliberate differences in form

- **Charts live in `outputs/charts/`**, not a `screenshots/` folder, and the chart set is financial:
  a cost-structure waterfall, a margin-by-discount-band chart, a diverging sub-category margin
  chart. Projects 1 and 3 have neither a waterfall nor a diverging profit chart.
- **The Excel workbook is a financial reporting pack** — Executive Summary, Cost Analysis,
  Profitability, Discount Analysis, Data Dictionary — rather than a segmentation workbook.
- **No Power BI in any form**, by instruction and because it cannot be verified here.

---

## Summary

| | Project 1 | Project 2 | Project 3 | Project 4 |
|---|---|---|---|---|
| Subject | wholesaler's customers | fast-food menus | marketplace growth | **retail financial performance** |
| Unit | customer | product | customer | **order-line margin** |
| Money in the data? | revenue only | none | revenue only | **revenue, discount, profit, cost** |
| Signature method | RFM segmentation | nutrition ratios | testing whether RFM applies | **margin decomposition and discount break-even** |
| Signature finding | 18% of customers = 60% of revenue | McDonald's carries 184 products vs 113–123 | 97% never return | **18.72% of lines sold below cost; break-even at a 20% discount** |
| Audience | marketing | category management | growth / commercial | **finance and management** |
