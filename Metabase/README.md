@"
# Metabase Dashboards

This folder contains PDF exports of the three manager-facing Metabase dashboards used in the project.

## Dashboards

1. [Customer Churn Risk Dashboard](01_Customer_Churn_Risk_Dashboard.pdf)
2. [Customer LTV & Value Dashboard](02_Customer_LTV_Value_Dashboard.pdf)
3. [Churn Insights & Retention Strategy](03_Churn_Insights_Retention_Strategy.pdf)

Metabase is the primary manager-facing analytics interface. The dashboards are connected to the Neon PostgreSQL database and visualize the prediction data produced by the project pipeline.

## Data Flow

```text
Prediction Pipeline
        ↓
Neon PostgreSQL
        ↓
Metabase
        ↓
Manager Dashboards



## Metabase Dashboard
