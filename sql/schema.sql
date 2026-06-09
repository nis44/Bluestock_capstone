DROP TABLE IF EXISTS fact_sip_industry;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_portfolio;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_category_inflows;
DROP TABLE IF EXISTS fact_industry_folios;
DROP TABLE IF EXISTS fact_benchmark_indices;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_fund;

CREATE TABLE dim_fund (
    amfi_code TEXT PRIMARY KEY,
    fund_house TEXT,
    scheme_name TEXT,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    launch_date DATE,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

CREATE TABLE dim_date (
    date_id TEXT PRIMARY KEY,
    date DATE,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    month_name TEXT,
    is_weekday INTEGER
);

CREATE TABLE fact_nav (
    amfi_code TEXT,
    date_id TEXT,
    nav REAL,
    daily_return_pct REAL,
    PRIMARY KEY (amfi_code, date_id),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

CREATE TABLE fact_transactions (
    tx_id TEXT PRIMARY KEY,
    investor_id TEXT,
    transaction_date DATE,
    date_id TEXT,
    amfi_code TEXT,
    transaction_type TEXT,
    amount_inr REAL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

CREATE TABLE fact_performance (
    amfi_code TEXT PRIMARY KEY,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_portfolio (
    amfi_code TEXT,
    stock_symbol TEXT,
    stock_name TEXT,
    sector TEXT,
    weight_pct REAL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date DATE,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_aum (
    date_id TEXT,
    fund_house TEXT,
    aum_lakh_crore REAL,
    aum_crore REAL,
    num_schemes INTEGER,
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

CREATE TABLE fact_sip_industry (
    month TEXT PRIMARY KEY,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

CREATE TABLE fact_category_inflows (
    month TEXT,
    category TEXT,
    net_inflow_crore REAL
);

CREATE TABLE fact_industry_folios (
    month TEXT PRIMARY KEY,
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

CREATE TABLE fact_benchmark_indices (
    date_id TEXT,
    index_name TEXT,
    close_value REAL,
    daily_return_pct REAL,
    PRIMARY KEY (date_id, index_name),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

CREATE INDEX idx_fact_nav_amfi_date ON fact_nav(amfi_code, date_id);
CREATE INDEX idx_fact_transactions_state ON fact_transactions(state);
CREATE INDEX idx_fact_transactions_amfi_date ON fact_transactions(amfi_code, date_id);
CREATE INDEX idx_benchmark_index_date ON fact_benchmark_indices(index_name, date_id);
