-- 1. Top 5 funds by AUM
SELECT f.fund_house, f.scheme_name, p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month
SELECT substr(d.date, 1, 7) AS month, ROUND(AVG(n.nav), 2) AS avg_nav
FROM fact_nav n
JOIN dim_date d ON d.date_id = n.date_id
GROUP BY substr(d.date, 1, 7)
ORDER BY month;

-- 3. SIP inflow YoY growth
SELECT month, sip_inflow_crore, yoy_growth_pct
FROM fact_sip_industry
ORDER BY month;

-- 4. Transactions by state
SELECT state, COUNT(*) AS transaction_count, ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- 5. Funds with expense ratio below 1 percent
SELECT fund_house, scheme_name, plan, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1
ORDER BY expense_ratio_pct;

-- 6. Top 5 funds by Sharpe ratio
SELECT f.scheme_name, p.sharpe_ratio, p.return_3yr_pct, p.max_drawdown_pct
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
ORDER BY p.sharpe_ratio DESC
LIMIT 5;

-- 7. Category-wise average 3-year return
SELECT f.sub_category, ROUND(AVG(p.return_3yr_pct), 2) AS avg_return_3yr_pct
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
GROUP BY f.sub_category
ORDER BY avg_return_3yr_pct DESC;

-- 8. Investor transaction split by type
SELECT transaction_type, COUNT(*) AS transactions, ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount_inr DESC;

-- 9. Latest AUM by fund house
SELECT fund_house, aum_lakh_crore, aum_crore, num_schemes
FROM fact_aum
WHERE date_id = (SELECT MAX(date_id) FROM fact_aum)
ORDER BY aum_crore DESC;

-- 10. Benchmark return summary
SELECT index_name, ROUND(MIN(close_value), 2) AS min_close, ROUND(MAX(close_value), 2) AS max_close,
       ROUND(AVG(daily_return_pct), 4) AS avg_daily_return_pct
FROM fact_benchmark_indices
GROUP BY index_name
ORDER BY index_name;
