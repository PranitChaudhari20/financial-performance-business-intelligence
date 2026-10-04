# Limitations

*Author: Pranit Ajay Chaudhari*

An honest list. None of these is a defect in the work; each is a real boundary on what the data can
support, and each is stated because a recommendation built past it would be guesswork.

## The one that matters most: this is sample data

**Sample — Superstore is demonstration content published by Tableau for a fictional US retailer.**
It is not a real company's financial statements. Every figure in this project is computed honestly
from the file and nothing is invented — but the findings demonstrate financial-analysis **method**
rather than describing a real firm's performance. A reader should take the technique seriously and
the business conclusions as an exercise.

This is stated here, in `README.md` and in `data/raw/README.md` rather than left for a reader to
discover.

## What the dataset does not contain

- **No operating expenses, overheads, payroll, rent, marketing spend or tax.** So there is **no
  operating margin, no EBITDA and no net profit in the accounting sense** anywhere in this project,
  and none is estimated. The 12.47% figure is profit over net revenue at the order-line level, and
  nothing is known about whether it survives the costs of running the company.
- **No unit cost or supplier cost.** "Implied cost of sales" is a **residual** (`Revenue − Profit`),
  not a reported cost line. It cannot be split into product cost, fulfilment or anything else, and
  it silently absorbs whatever the publisher folded into its profit calculation.
- **No list price field.** Gross sales is recovered as `Sales / (1 − Discount)`. The identity is
  tested and holds for 98.3% of discounted products, but it is still a reconstruction.
- **No currency column.** The retailer is US-based and the amounts are read as US dollars
  throughout. The dataset does not say so; this is an assumption.
- **No returns, refunds or cancellations.** Revenue is gross of anything later sent back, so the
  real margin is at best the one reported here.
- **No budget or forecast**, so no variance analysis is possible.
- **No cost to serve per customer**, so a loss-making line cannot be weighed against the value of
  the customer who bought it. A line sold below cost may still be rational; this data cannot say.

## Method

- **Correlation, not causation.** Regions that discount more earn less, and the ordering is
  perfectly inverse across all four. That is consistent with discount policy driving margin, but the
  regions also differ in product mix, customer mix and state composition. The project says the
  association is worth investigating; it does not claim the mechanism.
- **The discount/margin relationship is observed, not causal either.** Deeper discounts may be
  granted *because* a product is hard to sell, so the discount could be a symptom as much as a
  cause. The break-even point is still a fact about the business as it currently trades.
- **Seasonality is tested within four years only.** Four observations per month is enough to say a
  month landed on the same side of its year's average every time, which is what is claimed. It is
  not enough to fit a seasonal model or to separate seasonality from a recurring commercial calendar
  (promotions, fiscal year-end) that happens to repeat.
- **Quadrant analysis uses median splits**, which are arbitrary in the sense that any threshold is.
  The thresholds are stated with the result so a reader can judge them.
- **One row is a duplicate on all columns except Row ID** and was kept, because the same product can
  legitimately appear twice on one order. If it is in fact a data error, it affects one line in
  9,994.

## Scope

- **No Power BI.** Power BI Desktop runs only on Windows and could not be created or verified in the
  environment this project was built in. Rather than ship files, DAX or screenshots nobody has
  checked, it is **not part of this project at all** — no `.pbix`, no `.pbip`, no `.dax`, and no
  claim that any dashboard was built.
- **No customer, marketing or growth analysis.** No segmentation, RFM, cohort, retention, campaign
  or acquisition work. Those belong to other projects in this portfolio; see
  `docs/DIFFERENTIATION.md`. `Segment` is used here only as a revenue and margin dimension.
- **United States only.** `Country` holds one value, so there is no international comparison.
