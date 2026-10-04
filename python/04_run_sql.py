"""
04_run_sql.py  -  build the database, load it, run every query, export the results
==================================================================================
Author: Pranit Ajay Chaudhari

Creates the star schema, loads the cleaned order lines into it, runs every query in
sql/analysis_queries.sql and writes each result set to sql/query_results/.

Loading is done with executemany() rather than LOAD DATA LOCAL INFILE so the script works on a
default MySQL or MariaDB install: LOAD DATA LOCAL INFILE needs local_infile enabled on BOTH the
client and the server, which is off by default on most installs and is a common reason a project
like this fails to reproduce on someone else's machine.

Usage:  python python/04_run_sql.py --user root --password "..." [--socket /path/mysqld.sock]
"""
import argparse
import csv
import re
import sys
from pathlib import Path

import pandas as pd

try:
    import pymysql
except ImportError:
    print("PyMySQL is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql"
OUT = SQL / "query_results"
OUT.mkdir(exist_ok=True)
CLEAN = ROOT / "data" / "cleaned" / "superstore_clean.csv"


def statements(text):
    cleaned = "\n".join(l for l in text.splitlines() if not l.strip().startswith("--"))
    return [s.strip() for s in re.split(r";\s*\n", cleaned) if s.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", default="root")
    ap.add_argument("--password", default="")
    ap.add_argument("--socket", default=None)
    a = ap.parse_args()

    if not CLEAN.exists():
        print(f"  {CLEAN.relative_to(ROOT)} not found - run python/01_clean_data.py first.")
        return 1

    d = pd.read_csv(CLEAN, parse_dates=["OrderDate", "ShipDate"])
    print(f"  cleaned data: {len(d):,} order lines")

    conn = pymysql.connect(host=a.host, port=a.port, user=a.user, password=a.password,
                           unix_socket=a.socket, autocommit=False, charset="utf8mb4")
    cur = conn.cursor()

    print("1/3  schema")
    for stmt in statements((SQL / "schema.sql").read_text(encoding="utf-8")):
        cur.execute(stmt)
    conn.commit()
    cur.execute("USE financial_performance")

    print("2/3  load")
    prod = d[["Product ID", "Category", "Sub-Category", "Product Name"]].drop_duplicates("Product ID")
    cur.executemany("INSERT INTO dim_product (product_id, category, sub_category, product_name) "
                    "VALUES (%s,%s,%s,%s)", prod.values.tolist())

    geo = d[["Region", "State", "City", "Postal Code"]].drop_duplicates().reset_index(drop=True)
    geo["Postal Code"] = geo["Postal Code"].astype(str)
    cur.executemany("INSERT INTO dim_geography (region, state, city, postal_code) "
                    "VALUES (%s,%s,%s,%s)", geo.values.tolist())
    cur.execute("SELECT geo_id, region, state, city, postal_code FROM dim_geography")
    geo_map = {(r[1], r[2], r[3], r[4]): r[0] for r in cur.fetchall()}

    dates = pd.DataFrame({"date_key": pd.date_range(d.OrderDate.min(), d.OrderDate.max(), freq="D")})
    dates["year"] = dates.date_key.dt.year
    dates["quarter"] = dates.date_key.dt.quarter
    dates["year_quarter"] = dates.date_key.dt.to_period("Q").astype(str)
    dates["month_num"] = dates.date_key.dt.month
    dates["month_name"] = dates.date_key.dt.strftime("%b")
    dates["month_key"] = dates.date_key.dt.to_period("M").astype(str)
    dates["date_key"] = dates.date_key.dt.date
    cur.executemany("INSERT INTO dim_date (date_key, year, quarter, year_quarter, month_num, "
                    "month_name, month_key) VALUES (%s,%s,%s,%s,%s,%s,%s)", dates.values.tolist())

    fact = d.assign(geo_id=[geo_map[(r, s, c, str(p))] for r, s, c, p in
                            zip(d.Region, d.State, d.City, d["Postal Code"])])
    rows = fact[["Row ID", "Order ID", "OrderDate", "ShipDate", "Ship Mode", "Customer ID",
                 "Segment", "Product ID", "geo_id", "Quantity", "Discount", "DiscountBand",
                 "GrossSales", "DiscountValue", "Revenue", "ImpliedCost", "Profit",
                 "IsLossMaking"]].copy()
    rows["OrderDate"] = rows.OrderDate.dt.date
    rows["ShipDate"] = rows.ShipDate.dt.date
    rows["IsLossMaking"] = rows.IsLossMaking.astype(int)
    cur.executemany(
        "INSERT INTO fact_order_lines (row_id, order_id, order_date, ship_date, ship_mode, "
        "customer_id, segment, product_id, geo_id, quantity, discount, discount_band, gross_sales, "
        "discount_value, revenue, implied_cost, profit, is_loss_making) "
        "VALUES (" + ",".join(["%s"] * 18) + ")", rows.values.tolist())
    conn.commit()

    cur.execute("SELECT (SELECT COUNT(*) FROM fact_order_lines), (SELECT COUNT(*) FROM dim_product), "
                "(SELECT COUNT(*) FROM dim_geography), (SELECT COUNT(*) FROM dim_date), "
                "(SELECT ROUND(SUM(revenue),2) FROM fact_order_lines), "
                "(SELECT ROUND(SUM(profit),2) FROM fact_order_lines)")
    chk = cur.fetchone()
    print(f"     self-check: {chk[0]:,} fact rows | {chk[1]:,} products | {chk[2]:,} geographies | "
          f"{chk[3]:,} dates | revenue {chk[4]:,} | profit {chk[5]:,}")

    print("3/3  queries")
    blocks = re.split(r"^-- QUERY ", (SQL / "analysis_queries.sql").read_text(encoding="utf-8"),
                      flags=re.M)[1:]
    for block in blocks:
        header, body = block.split("\n", 1)
        num, title, _q = [p.strip() for p in header.split("|")]
        stmt = "\n".join(l for l in body.splitlines()
                         if not l.strip().startswith("--")).strip().rstrip(";")
        cur.execute(stmt)
        cols = [c[0] for c in cur.description]
        res = cur.fetchall()
        slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
        path = OUT / f"q{num}_{slug}.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(res)
        print(f"     Q{num} {title:<34} {len(res):>3} rows -> {path.relative_to(ROOT)}")

    conn.close()
    print("\n  All SQL executed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
