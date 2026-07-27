# Day 1 - Data Ingestion Notes

## Datasets Loaded (10/10, all successful)
01_fund_master (40, 15), 02_nav_history (46000, 3), 03_aum_by_fund_house (90, 5),
04_monthly_sip_inflows (48, 6), 05_category_inflows (144, 3),
06_industry_folio_count (21, 6), 07_scheme_performance (40, 19),
08_investor_transactions (32778, 13), 09_portfolio_holdings (322, 8),
10_benchmark_indices (8050, 3)

## Fund Master Structure
- 10 fund houses, 2 categories (Equity, Debt), 12 sub-categories, 5 risk levels
- SEBI category codes follow pattern: [Asset Class Letter][Type Letter][Number]
  e.g. EC01 = Equity/Cap-based/Large Cap, DC02 = Debt/Cap-based/Gilt, EI01 = Equity/Index

## AMFI Code Validation
- fund_master (40 schemes) and nav_history (40 schemes) match exactly — zero mismatches.
- All 32,778 investor_transactions reference valid amfi_codes from fund_master.
- NAV history is perfectly even: exactly 1,150 records per scheme, no gaps.

## Anomalies Found
- 04_monthly_sip_inflows: 12 missing values in yoy_growth_pct — expected, since the
  first 12 months (Jan-Dec 2022) have no prior year to compute YoY growth against.
- All date columns (date, launch_date, transaction_date, month, portfolio_date)
  loaded as string/object type — will need pd.to_datetime() conversion before any
  time-series analysis (sorting, trend plots, date-range joins).
- fund_master uses column name 'risk_category', scheme_performance uses 'risk_grade'
  for the same concept — needs standardizing before merging the two tables.

## Data Quality Summary
Data quality is excellent — zero duplicate rows, near-zero missing values, and 100%
referential integrity between fund_master, nav_history, and investor_transactions on
amfi_code. Main pre-processing work needed before analysis: convert date columns to
datetime, and standardize the risk_category/risk_grade column naming mismatch.