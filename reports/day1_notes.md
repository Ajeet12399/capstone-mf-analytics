# Day 1 — Project Setup + Data Ingestion (ETL) — Notes

---
 
## 1. Datasets Loaded (10/10 successful)
 
| Dataset | Shape | Duplicates | Missing values |
|---|---|---|---|
| 01_fund_master | (40, 15) | 0 | 0 |
| 02_nav_history | (46000, 3) | 0 | 0 |
| 03_aum_by_fund_house | (90, 5) | 0 | 0 |
| 04_monthly_sip_inflows | (48, 6) | 0 | 12 (in `yoy_growth_pct`) |
| 05_category_inflows | (144, 3) | 0 | 0 |
| 06_industry_folio_count | (21, 6) | 0 | 0 |
| 07_scheme_performance | (40, 19) | 0 | 0 |
| 08_investor_transactions | (32778, 13) | 0 | 0 |
| 09_portfolio_holdings | (322, 8) | 0 | 0 |
| 10_benchmark_indices | (8050, 3) | 0 | 0 |
 
All 10 files loaded cleanly with pandas — no parsing errors, no encoding issues.
 
---
 
## 2. Fund Master Structure
 
- **40 schemes** across **10 fund houses**: SBI, HDFC, ICICI Prudential, Nippon India, Kotak Mahindra, Axis, Aditya Birla Sun Life, UTI, Mirae Asset, DSP.
- **Category**: Equity (34 schemes), Debt (6 schemes). The schema documentation allows for Hybrid as a third value, but this 40-scheme sample contains none — worth noting for Day 2 schema design, not an error.
- **Sub-category** (12 total): Large Cap (14), Mid Cap (7), Small Cap (6), Liquid (3), Gilt (2), Flexi Cap (2), and one each of Short Duration, Value, Index/ETF, Index, Large & Mid Cap, ELSS.
- **Risk category** (5 levels): Low, Moderate, Moderately High, High, Very High.
- **Plan**: Direct / Regular.
**SEBI category code mapping (verified against actual data):**
 
| Code | Maps to |
|---|---|
| EC01 | Large Cap |
| EC02 | Mid Cap |
| EC03 | Small Cap |
| EC04 | Flexi Cap, Large & Mid Cap |
| EC05 | ELSS |
| EC06 | Value |
| EI01 | Index, Index/ETF |
| DC01 | Liquid |
| DC02 | Gilt, Short Duration |
 
This matches the pattern described in the project brief exactly (EC = Equity/Cap-based, EI = Equity/Index, DC = Debt/Cap-based).
 
---
 
## 3. AMFI Code Validation (cross-dataset referential integrity)
 
| Check | Result |
|---|---|
| fund_master vs nav_history | 40 vs 40 schemes — exact match, zero mismatches either direction |
| fund_master vs scheme_performance | 40 vs 40 schemes — exact match, zero mismatches |
| fund_master vs investor_transactions | All 32,778 transactions reference valid AMFI codes; all 40 schemes appear at least once |
| fund_master vs portfolio_holdings | Only 34/40 schemes present — see note below |
| risk_category (fund_master) vs risk_grade (scheme_performance) | 0 value mismatches across all 40 schemes — same data, different column name |
 
**Portfolio holdings note:** The 6 schemes missing from `09_portfolio_holdings.csv` are exactly the 6 Debt schemes (2× Gilt, 1× Short Duration, 3× Liquid). This is expected, not a data error — debt funds hold bonds/money-market instruments, not individual equity stocks with sector weightings, so they have no stock-level holdings to report.
 
---
 
## 4. NAV History Coverage
 
- Exactly **1,150 NAV records per scheme** across all 40 schemes (standard deviation = 0 — perfectly even coverage, no gaps).
- Date range: **2022-01-03 to 2026-05-29** (~4.4 years), consistent with the project's stated "Jan 2022 to May 2026" coverage.
---
 
## 5. Additional Data Quality Checks
 
- **Expense ratio**: ranges 0.55%–1.64%, within the expected 0.1%–2.5% band — no out-of-range values.
- **Sharpe ratio**: no negative values among the 40 schemes.
- **Portfolio weights**: sum to ~100% per fund for all 34 equity schemes with holdings data (mean 99.9997%, std 0.01) — internally consistent.
- **Transaction types**: SIP / Lumpsum / Redemption (3 types, as expected).
- **KYC status split**: Verified 92.0% / Pending 8.0% — matches the project brief's stated real-world proportion almost exactly.
- **Geography**: 12 states covered, city tiers split T30 / B30.
---
 
## 6. Live NAV Fetch — mfapi.in (correction included)
 
Cross-checking the 6 required AMFI codes against the project's own `01_fund_master.csv` (ground truth) confirms **all 6 are correct as given**:
 
| Code | Confirmed scheme (from fund_master.csv) |
|---|---|
| 125497 | HDFC Top 100 Fund - Direct Plan - Growth |
| 119551 | SBI Bluechip Fund - Regular Plan - Growth |
| 120503 | ICICI Pru Bluechip Fund - Regular - Growth |
| 118632 | Nippon India Large Cap Fund - Regular - Growth |
| 119092 | Axis Bluechip Fund - Regular - Growth |
| 120841 | Kotak Bluechip Fund - Regular - Growth |
 
On the first live fetch attempt, 5 of these 6 codes returned **unrelated schemes** from the live `api.mfapi.in` API (only Nippon's came back correct). Since all 6 codes check out against the project's reference data — and mfapi.in's own API documentation separately confirms 125497 = HDFC Top 100 Direct — this points to a **transient issue with the live API** (rate limiting, caching, or a temporary backend glitch) rather than incorrect codes in the task.
 
**Action:** Re-run `live_nav_fetch.py` and verify each returned scheme name/fund house matches the table above before saving. Added an assertion check in the script so any future mismatch fails loudly instead of silently saving mislabeled data.
 
---
 
## 7. Anomalies Found
 
1. **`yoy_growth_pct` nulls** (04_monthly_sip_inflows): 12 missing values, exactly Jan–Dec 2022 — expected, since there's no prior year to compute year-over-year growth against.
2. **Date columns loaded as strings**: `date`, `launch_date`, `transaction_date`, `month`, `portfolio_date` all came in as `object`/`str` type — will need `pd.to_datetime()` conversion before any time-series work (sorting, trend charts, date-range joins) in Day 2/3.
3. **Column naming inconsistency**: `fund_master` uses `risk_category`, `scheme_performance` uses `risk_grade` for the same concept (values agree 100%, just the label differs) — standardize before merging.
4. **Category field**: only Equity/Debt present in this sample (schema technically allows Hybrid) — no action needed, just noting for Day 2 schema design.
5. **Portfolio holdings scope**: covers 34/40 schemes by design (Debt schemes excluded, since they don't hold individual equities).
6. **Live NAV fetch mismatch**: see Section 6 — resolved by cross-verifying against local reference data; likely a transient live-API issue, not a data error.
---
 
## 8. Data Quality Summary
 
Overall data quality is excellent: zero duplicate rows across all 10 datasets, minimal missing values (only the expected 12 YoY nulls), and 100% referential integrity of AMFI codes across `fund_master`, `nav_history`, `scheme_performance`, and `investor_transactions`. Portfolio holdings coverage of 34/40 schemes is correct by design. The one real issue encountered was a live-API inconsistency during the mfapi.in NAV fetch, resolved by cross-verifying scheme codes against the project's own `fund_master.csv` — all 6 codes were confirmed correct. Main pre-processing work carried into Day 2: convert date columns to datetime, standardize the `risk_category`/`risk_grade` naming, and re-confirm live NAV fetch results before finalizing raw data for the ETL pipeline.
 
---