# Data Dictionary

## fund_master

| Column | Type | Nulls |
|---|---:|---:|
| `amfi_code` | `object` | 0 |
| `fund_house` | `object` | 0 |
| `scheme_name` | `object` | 0 |
| `category` | `object` | 0 |
| `sub_category` | `object` | 0 |
| `plan` | `object` | 0 |
| `launch_date` | `object` | 0 |
| `benchmark` | `object` | 0 |
| `expense_ratio_pct` | `float64` | 0 |
| `exit_load_pct` | `float64` | 0 |
| `min_sip_amount` | `int64` | 0 |
| `min_lumpsum_amount` | `int64` | 0 |
| `fund_manager` | `object` | 0 |
| `risk_category` | `object` | 0 |
| `sebi_category_code` | `object` | 0 |

## nav_history

| Column | Type | Nulls |
|---|---:|---:|
| `amfi_code` | `object` | 0 |
| `date_id` | `object` | 0 |
| `date` | `object` | 0 |
| `nav` | `float64` | 0 |
| `daily_return_pct` | `float64` | 0 |

## aum

| Column | Type | Nulls |
|---|---:|---:|
| `date_id` | `object` | 0 |
| `date` | `object` | 0 |
| `fund_house` | `object` | 0 |
| `aum_lakh_crore` | `float64` | 0 |
| `aum_crore` | `int64` | 0 |
| `num_schemes` | `int64` | 0 |

## sip

| Column | Type | Nulls |
|---|---:|---:|
| `month` | `object` | 0 |
| `sip_inflow_crore` | `int64` | 0 |
| `active_sip_accounts_crore` | `float64` | 0 |
| `new_sip_accounts_lakh` | `float64` | 0 |
| `sip_aum_lakh_crore` | `float64` | 0 |
| `yoy_growth_pct` | `float64` | 12 |

## category_inflows

| Column | Type | Nulls |
|---|---:|---:|
| `month` | `object` | 0 |
| `category` | `object` | 0 |
| `net_inflow_crore` | `float64` | 0 |

## folios

| Column | Type | Nulls |
|---|---:|---:|
| `month` | `object` | 0 |
| `total_folios_crore` | `float64` | 0 |
| `equity_folios_crore` | `float64` | 0 |
| `debt_folios_crore` | `float64` | 0 |
| `hybrid_folios_crore` | `float64` | 0 |
| `others_folios_crore` | `float64` | 0 |

## performance

| Column | Type | Nulls |
|---|---:|---:|
| `amfi_code` | `object` | 0 |
| `scheme_name` | `object` | 0 |
| `fund_house` | `object` | 0 |
| `category` | `object` | 0 |
| `plan` | `object` | 0 |
| `return_1yr_pct` | `float64` | 0 |
| `return_3yr_pct` | `float64` | 0 |
| `return_5yr_pct` | `float64` | 0 |
| `benchmark_3yr_pct` | `float64` | 0 |
| `alpha` | `float64` | 0 |
| `beta` | `float64` | 0 |
| `sharpe_ratio` | `float64` | 0 |
| `sortino_ratio` | `float64` | 0 |
| `std_dev_ann_pct` | `float64` | 0 |
| `max_drawdown_pct` | `float64` | 0 |
| `aum_crore` | `int64` | 0 |
| `expense_ratio_pct` | `float64` | 0 |
| `morningstar_rating` | `int64` | 0 |
| `risk_grade` | `object` | 0 |

## transactions

| Column | Type | Nulls |
|---|---:|---:|
| `tx_id` | `object` | 0 |
| `investor_id` | `object` | 0 |
| `transaction_date` | `object` | 0 |
| `date_id` | `object` | 0 |
| `amfi_code` | `object` | 0 |
| `transaction_type` | `object` | 0 |
| `amount_inr` | `int64` | 0 |
| `state` | `object` | 0 |
| `city` | `object` | 0 |
| `city_tier` | `object` | 0 |
| `age_group` | `object` | 0 |
| `gender` | `object` | 0 |
| `annual_income_lakh` | `float64` | 0 |
| `payment_mode` | `object` | 0 |
| `kyc_status` | `object` | 0 |

## portfolio

| Column | Type | Nulls |
|---|---:|---:|
| `amfi_code` | `object` | 0 |
| `stock_symbol` | `object` | 0 |
| `stock_name` | `object` | 0 |
| `sector` | `object` | 0 |
| `weight_pct` | `float64` | 0 |
| `market_value_cr` | `float64` | 0 |
| `current_price_inr` | `float64` | 0 |
| `portfolio_date` | `object` | 0 |

## benchmarks

| Column | Type | Nulls |
|---|---:|---:|
| `date_id` | `object` | 0 |
| `date` | `object` | 0 |
| `index_name` | `object` | 0 |
| `close_value` | `float64` | 0 |
| `daily_return_pct` | `float64` | 0 |

## dim_date

| Column | Type | Nulls |
|---|---:|---:|
| `date_id` | `object` | 0 |
| `date` | `object` | 0 |
| `year` | `int32` | 0 |
| `month` | `int32` | 0 |
| `quarter` | `int32` | 0 |
| `month_name` | `object` | 0 |
| `is_weekday` | `int64` | 0 |
