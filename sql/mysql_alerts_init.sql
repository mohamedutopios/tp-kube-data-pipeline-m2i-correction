CREATE DATABASE IF NOT EXISTS alerts;
USE alerts;
CREATE TABLE IF NOT EXISTS suspicious_transactions(
  id VARCHAR(36) PRIMARY KEY,
  ts_utc TIMESTAMP,
  datetime_norm VARCHAR(32),
  creditor_name VARCHAR(128),
  creditor_account VARCHAR(64),
  creditor_country VARCHAR(8),
  debtor_name VARCHAR(128),
  debtor_account VARCHAR(64),
  debtor_country VARCHAR(8),
  amount_usd DECIMAL(18,2),
  agent_first VARCHAR(64),
  agent_last  VARCHAR(64)
);
