# Business insights

*Author: Pranit Ajay Chaudhari*

Each insight separates three things deliberately: the **finding** (what the data says), the
**supporting metric** (the number, computed from the data and reproduced in three tools), and the
**interpretation** (what it could mean for management — judgement, not fact). Every figure comes
from `outputs/csv/` and is cross-checked by `python/06_verify.py`.

Amounts are in US dollars, the currency convention for this US retailer. The dataset does not state
a currency; see `docs/LIMITATIONS.md`.

---

## 1. Discounting is where the money goes

**Finding.** Net margin falls monotonically as the discount rate rises, and turns negative above a
20% discount. Every order line discounted more than 50% loses money.

**Supporting metric.**

| Discount band | Order lines | Net revenue | Profit | Net margin | Loss-making lines |
|---|---|---|---|---|---|
| 0% | 4,798 | 1,087,908.47 | 320,987.60 | **29.51%** | 0.00% |
| 1–10% | 94 | 54,369.35 | 9,029.18 | 16.61% | 4.26% |
| 11–20% | 3,709 | 792,152.89 | 91,756.30 | 11.58% | 13.99% |
| 21–30% | 227 | 103,226.66 | −10,369.28 | **−10.05%** | 91.63% |
| 31–50% | 310 | 195,314.76 | −48,447.73 | −24.80% | 91.61% |
| over 50% | 856 | 64,228.74 | −76,559.05 | **−119.20%** | **100.00%** |

At the exact rates, margin is positive up to and including 20% and negative from 30% upward.
Across the business, **19.79%** of list value is given away as discount — **566,734.18** in total.

**Interpretation.** The product set is not the problem: undiscounted business runs at a 29.51%
margin. The problem is the discount approval policy. A hard cap at 20%, with anything beyond it
requiring explicit sign-off, addresses the single largest identified drain. Note the asymmetry —
the "over 50%" band is only 2.8% of gross sales but destroys 76,559 of profit.

## 2. Almost one order line in five is sold below cost

**Finding.** 1,871 of 9,994 order lines are loss-making.

**Supporting metric.** **18.72%** of lines, giving back **−156,131.29** of profit. Total profit is
286,397.02, so the business earns roughly 442,528 and hands back just over a third of it.

**Interpretation.** This is the size of the prize. It does not mean those lines should all be
refused — some may be loss-leaders or contractual — but the business currently cannot tell which,
because nothing flags a line as below cost at the point of quoting. A margin check before the order
is confirmed converts this from a reporting finding into a control.

## 3. Furniture earns almost nothing

**Finding.** Furniture is the second largest category by revenue and the smallest by profit.

**Supporting metric.**

| Category | Revenue | % of revenue | Profit | % of profit | Net margin |
|---|---|---|---|---|---|
| Technology | 836,154.03 | 36.40% | 145,454.95 | 50.79% | 17.40% |
| Furniture | 741,999.80 | **32.30%** | 18,451.27 | **6.44%** | **2.49%** |
| Office Supplies | 719,047.03 | 31.30% | 122,490.80 | 42.77% | 17.04% |

Furniture carries a third of revenue and a sixteenth of profit; its margin is a seventh of
Technology's. **33.66%** of its order lines lose money, against roughly 14.7% in each of the other
two categories.

**Interpretation.** A third of the business is being run close to break-even. The question for
management is whether Furniture is a deliberate traffic-builder — in which case its margin should
be budgeted and monitored as such — or an unmanaged drift. The sub-category detail below suggests
the latter, because the losses are concentrated rather than spread.

## 4. Three sub-categories lose money outright

**Finding.** Tables, Bookcases and Supplies each return a negative margin across the whole period.

**Supporting metric.**

| Sub-category | Revenue | Profit | Net margin | Discount rate | Loss-making lines |
|---|---|---|---|---|---|
| Tables | 206,965.53 | −17,725.48 | **−8.56%** | 25.47% | 63.64% |
| Bookcases | 114,880.00 | −3,472.56 | −3.02% | 22.46% | 47.81% |
| Supplies | 46,673.54 | −1,189.10 | −2.55% | 7.49% | 17.37% |

Together: **−22,387.14** on **368,519.07** of revenue — 16.0% of total revenue earning nothing.

**Interpretation.** Tables and Bookcases are both discounted far above the 20% break-even point
(25.47% and 22.46%), and nearly two thirds of Table lines lose money. These two look like a pricing
problem rather than a product problem, and are the obvious first place to apply the discount cap
from insight 1. Supplies is a different case — its discount rate is low at 7.49%, so its thin loss
is not discount-driven and needs a cost or pricing review instead.

## 5. Six sub-categories carry 60% of revenue at a 5.35% margin

**Finding.** Splitting the 17 sub-categories at their median revenue and median margin puts most of
the revenue in the weakest quadrant.

**Supporting metric.**

| Quadrant | Sub-categories | Revenue | % of revenue | Net margin |
|---|---|---|---|---|
| High revenue, **low margin** | 6 | 1,393,383.92 | **60.66%** | **5.35%** |
| High revenue, high margin | 3 | 520,321.08 | 22.65% | 24.56% |
| Low revenue, high margin | 6 | 245,117.15 | 10.67% | 29.45% |
| Low revenue, low margin | 2 | 138,378.70 | 6.02% | 8.58% |

**Interpretation.** The revenue base and the profit base are different parts of the catalogue. Six
lines generate three fifths of turnover at a margin a fifth of what the healthy lines earn. Moving
that 5.35% up by even two points is worth more than growing the high-margin tail, simply because of
the revenue it sits on.

## 6. The region that discounts most earns least

**Finding.** Regional margin tracks the regional discount rate inversely.

**Supporting metric.**

| Region | Revenue | % of revenue | Profit | Net margin | Discount rate |
|---|---|---|---|---|---|
| West | 725,457.82 | 31.58% | 108,418.45 | **14.94%** | **15.55%** |
| East | 678,781.24 | 29.55% | 91,522.78 | 13.48% | 19.46% |
| South | 391,721.91 | 17.05% | 46,749.43 | 11.93% | 21.28% |
| Central | 501,239.89 | 21.82% | 39,706.36 | **7.92%** | **24.56%** |

Central is 21.82% of revenue and 13.86% of profit. It discounts 9 percentage points harder than
West and earns roughly half the margin.

**Interpretation.** The ordering is perfectly inverse across all four regions, which is consistent
with discount policy being set or enforced differently by region. It is association, not proof —
the regions also differ in product mix — but it is a specific, testable question to put to the
Central sales management.

## 7. Ten states lose money, and all of them discount heavily

**Finding.** 10 of 49 states return a negative profit.

**Supporting metric.** Combined loss **−98,246.74**. The largest: Texas −25,729.36 (39.06% discount
rate), Ohio −16,971.38 (41.98%), Pennsylvania −15,559.96 (37.83%), Illinois −12,607.89 (39.92%).
**Every one of the ten discounts at least 29% of list value**, against a company average of 19.79%.

**Interpretation.** These losses are not spread thinly — four states account for 71% of them, and
all four sit near or above a 38% discount rate. That makes this an enforceable short list rather
than a vague problem: four conversations, not forty-nine.

## 8. Revenue grew 14.83% a year while margin stayed flat

**Finding.** Revenue grew in three of four years; margin moved within a 3.2-point band and ended
below where it peaked.

**Supporting metric.**

| Year | Revenue | Growth | Implied cost | Cost growth | Profit | Net margin |
|---|---|---|---|---|---|---|
| 2014 | 484,247.50 | — | 434,703.52 | — | 49,543.97 | 10.23% |
| 2015 | 470,532.51 | −2.83% | 408,913.91 | −5.93% | 61,618.60 | 13.10% |
| 2016 | 609,205.60 | +29.47% | 527,410.42 | +28.98% | 81,795.17 | 13.43% |
| 2017 | 733,215.26 | +20.36% | 639,775.99 | +21.31% | 93,439.27 | 12.74% |

Revenue CAGR 2014–2017: **14.83%**. Cost-to-revenue sat between 86.57% and 89.77% throughout.

**Interpretation.** Growth is real and cost has tracked it almost exactly — in 2017 cost grew
slightly faster than revenue (21.31% against 20.36%), which is why margin slipped 0.69 points. The
business is scaling without improving its unit economics. That is survivable while growth continues
and becomes a problem the moment it stops.

## 9. Three months beat their own year's average, every year

**Finding.** September, November and December were above their year's monthly average in **all four
years**; January, February, April, June and July were below in all four.

**Supporting metric.** Mean index against each year's own average (100 = that year's average):
November 184.7, December 172.9, September 164.0 · February 30.1, January 47.5, April 73.4.

**Interpretation.** This is a tested pattern rather than an eyeballed one — indexing within each
year prevents growth from being mistaken for season. The practical use is working-capital and
staffing planning: three months carry a disproportionate share and five are reliably quiet. Note
that the Q4 peak coincides with the weakest margin quarter of 2017 (9.80%), which is worth
investigating as possible seasonal discounting.

## 10. Revenue is concentrated in a small part of the catalogue

**Finding.** 133 of 1,862 products produce half of all revenue.

**Supporting metric.** Top 10% of products = **59.09%** of revenue; top 20% = **77.45%**.
**301 products (16.17%)** lose money, costing **−76,721.13** between them.

**Interpretation.** A long tail of 1,729 products contributes under half the revenue and includes
301 that destroy value. Rationalising the tail is a lower-risk lever than repricing the core,
because the revenue at stake per decision is small — but it needs the loss-making products
identified individually, which `outputs/csv/worst_products_by_profit.csv` does.

---

## What management should look at first

In order of size, and all of them actionable from the numbers above:

1. **Cap discretionary discounting at 20%.** The break-even point is measured, not assumed.
2. **Flag below-cost lines before the order is confirmed**, not in the monthly report.
3. **Reprice Tables and Bookcases**, which are both discounted past break-even.
4. **Ask Central region why its discount rate is 9 points above West's.**
5. **Review the four states carrying 71% of the state-level losses.**
6. **Decide whether Furniture is a deliberate traffic-builder**; if it is, budget its margin.

## What the data cannot tell management

No operating expenses, so no view of whether the 12.47% net margin survives overheads. No unit
costs, so "implied cost" cannot be split into product cost versus fulfilment. No returns data. No
budget, so no variance analysis. And no customer-level cost to serve, so a loss-making line cannot
be judged against the lifetime value of the customer who bought it. These are set out in
`docs/LIMITATIONS.md`.
