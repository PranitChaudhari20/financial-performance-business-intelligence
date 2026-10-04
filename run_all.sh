#!/usr/bin/env bash
# =============================================================================
# run_all.sh  -  reproduce the whole project from the raw file
# Author: Pranit Ajay Chaudhari
#
# Run this from a fresh extraction. It takes about a minute, plus a few seconds
# for the Excel recalculation.
#
# The SQL step needs a running MySQL 8 or MariaDB server. Supply credentials
# through the environment and it runs; leave them unset and it is skipped with a
# clear message, and the committed query results in sql/query_results/ are used
# for verification instead.
#
#   MYSQL_USER=root MYSQL_PASSWORD=secret bash run_all.sh
#   MYSQL_SOCKET=/run/mysqld/mysqld.sock MYSQL_USER=root bash run_all.sh
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1/7  prepare raw data (privacy step) ======================================"
python python/00_prepare_raw.py

echo
echo "== 2/7  clean and validate ==================================================="
python python/01_clean_data.py

echo
echo "== 3/7  financial analysis ==================================================="
python python/02_analysis.py

echo
echo "== 4/7  charts ==============================================================="
python python/03_build_charts.py

echo
echo "== 5/7  SQL =================================================================="
if [ -n "${MYSQL_USER:-}" ]; then
  ARGS=(--user "$MYSQL_USER" --password "${MYSQL_PASSWORD:-}")
  [ -n "${MYSQL_SOCKET:-}" ] && ARGS+=(--socket "$MYSQL_SOCKET")
  [ -n "${MYSQL_HOST:-}" ]   && ARGS+=(--host "$MYSQL_HOST")
  python python/04_run_sql.py "${ARGS[@]}"
else
  echo "   SKIPPED: no MYSQL_USER set, so the database was not rebuilt."
  echo "   The committed results in sql/query_results/ are used for verification."
  echo "   To run it:  MYSQL_USER=root MYSQL_PASSWORD=... bash run_all.sh"
fi

echo
echo "== 6/7  Excel workbook ======================================================="
python python/05_build_excel.py
python python/07_recalc_excel.py

echo
echo "== 7/7  cross-tool verification =============================================="
set +e
python python/06_verify.py
VERIFY=$?
set -e
echo
case $VERIFY in
  0) echo "RESULT: every check passed." ;;
  2) echo "RESULT: figures agree where they could be checked, but the Excel workbook was not"
     echo "        recalculated (LibreOffice not found), so its checks did not run." ;;
  *) echo "RESULT: at least one figure disagrees - see the FAIL lines above."; exit $VERIFY ;;
esac
