# Day 2 Cleaning Report

| Dataset | Raw Rows | Clean Rows |
|---|---:|---:|
| fund_master | 40 | 40 |
| nav_history | 46,000 | 46,000 |
| aum | 90 | 90 |
| sip | 48 | 48 |
| category_inflows | 144 | 144 |
| folios | 21 | 21 |
| performance | 40 | 40 |
| transactions | 32,778 | 32,778 |
| portfolio | 322 | 322 |
| benchmarks | 8,050 | 8,050 |

## Validation Notes

- NAV values are numeric and greater than zero.
- Transaction amounts are positive and transaction types are standardized to SIP, Lumpsum, and Redemption.
- AMFI codes are stored as text to preserve key consistency across files.
- Daily return percentages were computed for NAV and benchmark series.
- SQLite database was rebuilt from the cleaned CSV outputs.