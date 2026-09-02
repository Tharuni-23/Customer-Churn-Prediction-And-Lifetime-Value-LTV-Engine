ALTER TABLE customer_churn
ADD COLUMN predicted_churn VARCHAR(10),
ADD COLUMN churn_probability NUMERIC(5,4),
ADD COLUMN predicted_ltv NUMERIC(12,2),
ADD COLUMN prediction_at TIMESTAMP;