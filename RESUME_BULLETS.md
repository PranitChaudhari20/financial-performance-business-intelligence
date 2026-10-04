# Résumé bullets

*Author: Pranit Ajay Chaudhari*

Every number below comes from `outputs/csv/` and reproduces in Python, MySQL and Excel. Nothing is
rounded in my favour or stated more strongly than the data supports.

---

## The project line

**Financial Performance & Business Intelligence Analytics** · Python, MySQL, Excel

---

## Three bullets (recommended set)

- Analysed **9,994 order lines across 48 continuous months ($2.86M gross sales, $2.30M net
  revenue)** in Python and a **4-table MySQL star schema**, building a full cost structure from list
  price to profit and finding that **18.72% of order lines were sold below cost**, handing back
  **$156,131** of profit.
- Identified the break-even point of the company's discounting policy by measuring margin at every
  discount rate — **+29.51% at no discount, turning negative above 20%, and −119.20% beyond 50%** —
  and traced **$98,247** of losses across ten states that all discounted at least 29% of list value.
- Built a **10-sheet Excel reporting pack and 16 SQL business queries**, and wrote an automated
  verifier that reconciles **94 figures across Python, SQL and Excel**; it caught two real defects,
  including workbook labels being parsed as formulas, which were fixed in the code.

---

## Shorter two-bullet version

- Built an end-to-end financial performance analysis of **9,994 order lines over four years** in
  **Python, MySQL and Excel**, deriving gross sales, discount, implied cost and margin, and showing
  that **almost one line in five was sold below cost** and that **margin turns negative above a 20%
  discount**.
- Isolated where profit was being lost — **Furniture at a 2.49% margin on 32% of revenue**, three
  loss-making sub-categories, and ten loss-making states — and delivered a KPI pack with **94
  automated cross-tool verification checks**.

---

## One-line version

Financial performance analysis of **9,994 order lines and $2.30M of revenue** in **Python, MySQL and
Excel**, quantifying a **$156,131 margin leak from below-cost selling** and establishing a **20%
discount break-even point** for management.

---

## Interview talking points

**"What did you actually find?"**
That the business was growing revenue 14.83% a year while its margin stayed flat, and that the
reason was discounting. I measured margin at every discount rate and it crosses zero between 20%
and 30% — at no discount the business runs at 29.5%, above 50% discount it runs at −119%. Nearly a
fifth of all order lines were sold below cost. That turns a vague "we discount too much" into a
specific policy: cap discretionary discounts at 20% and flag below-cost lines before the order is
confirmed, not in the monthly report.

**"How do you know your numbers are right?"**
I computed everything three times — pandas, SQL and Excel formulas — and wrote a script comparing
all 94 figures that fails if any disagree. The workbook doesn't display numbers copied from Python;
it recomputes them with its own SUMIFs, so a disagreement would surface. It caught two real bugs:
two row labels I'd written as "= Net revenue" were being parsed as formulas and wrote #VALUE! into
the file, and a distinct-order count I'd written as an array formula would have needed about 100
million operations to recalculate.

**"How did you choose the dataset?"**
I profiled a bigger one first — 180,000 rows, published with a DOI — and rejected it. When I counted
rows by market and month, the file turned out to be partitioned by market: most months contained
only one region. A revenue trend built on it would have measured the file's structure, not the
business. I went with the smaller dataset because it has 48 genuinely continuous months, and
documented why.

**"What can't your analysis tell us?"**
It has no operating expenses, so I can't say whether the 12.47% margin survives overheads — there's
no operating margin or EBITDA anywhere in the project and I didn't estimate one. "Implied cost" is a
residual, revenue minus profit, not a reported cost line, and I labelled it that way every time. And
it's sample data for a fictional retailer, so it demonstrates the method rather than describing a
real company.

**"Why is this different from your other projects?"**
My first and third projects both state in their own documentation that they can't measure
profitability — their datasets have no cost. This one is built entirely on that axis: cost
structure, margin, discount break-even and contribution by product and region. Different unit of
analysis too: those analyse customers, this analyses the margin on an order line.

---

## Skills this demonstrates

**Business:** financial statement logic and margin decomposition · cost structure analysis ·
pricing and discount policy · contribution analysis by product and region · KPI design for
management reporting · separating a finding from its interpretation · knowing which metrics a
dataset does and does not support.

**Technical:** Python (pandas, numpy, matplotlib, openpyxl) · SQL (star-schema design, foreign keys,
CTEs, window functions) · dimensional modelling · Excel formula modelling · hypothesis-style testing
of a seasonal pattern · reproducible pipelines · automated cross-tool verification · data provenance
and PII handling.
