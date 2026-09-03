from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from . import database as db
from .prediction_pipeline import predict_customer


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Customer Churn & LTV API",
    description="API for Manager Dashboard",
    version="1.0.0"
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Customer Churn & LTV API is running"
    }


# ============================================================
# DATABASE HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    try:
        engine = db.get_engine()

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@app.get("/dashboard/summary")
def dashboard_summary():
    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                COUNT(*) AS total_customers,

                COUNT(*) FILTER (
                    WHERE "Churn" = 'Yes'
                ) AS churned_customers,

                COUNT(*) FILTER (
                    WHERE "Churn" = 'No'
                ) AS retained_customers,

                ROUND(
                    AVG("MonthlyCharges")::numeric,
                    2
                ) AS average_monthly_charges,

                ROUND(
                    SUM("MonthlyCharges")::numeric,
                    2
                ) AS total_monthly_revenue,

                ROUND(
                    AVG(churn_probability)::numeric,
                    4
                ) AS average_churn_probability,

                ROUND(
                    AVG(predicted_ltv)::numeric,
                    2
                ) AS average_predicted_ltv

            FROM customer_churn;
        """)

        with engine.connect() as connection:
            result = connection.execute(query)
            row = result.mappings().first()

        return dict(row)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# GET CUSTOMERS
# ============================================================

@app.get("/customers")
def get_customers():
    try:
        engine = db.get_engine()

        query = text("""
            SELECT *
            FROM customer_churn
            ORDER BY "customerID"
            LIMIT 100;
        """)

        with engine.connect() as connection:
            result = connection.execute(query)

            customers = [
                dict(row)
                for row in result.mappings()
            ]

        return {
            "count": len(customers),
            "customers": customers
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# GET SINGLE CUSTOMER
# ============================================================

@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    try:
        engine = db.get_engine()

        query = text("""
            SELECT *
            FROM customer_churn
            WHERE "customerID" = :customer_id;
        """)

        with engine.connect() as connection:
            result = connection.execute(
                query,
                {
                    "customer_id": customer_id
                }
            )

            row = result.mappings().first()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        return dict(row)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# DASHBOARD CUSTOMERS
# ============================================================

@app.get("/dashboard/customers")
def dashboard_customers():
    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                "customerID",
                "gender",
                "SeniorCitizen",
                "Partner",
                "Dependents",
                "tenure",
                "Contract",
                "MonthlyCharges",
                "TotalCharges",
                "Churn",
                "TenureGroup",
                "TotalServices",
                "Mails",
                predicted_churn,
                churn_probability,
                predicted_ltv,
                prediction_at
            FROM customer_churn
            ORDER BY "customerID"
            LIMIT 100;
        """)

        with engine.connect() as connection:
            result = connection.execute(query)

            customers = [
                dict(row)
                for row in result.mappings()
            ]

        return {
            "count": len(customers),
            "customers": customers
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# ============================================================
# PREDICT CUSTOMER
# ============================================================

@app.post("/predict/{customer_id}")
def predict_customer_api(customer_id: str):
    try:
        result = predict_customer(customer_id)

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# ============================================================
# CHURN RISK SUMMARY
# ============================================================

@app.get("/dashboard/risk-summary")
def dashboard_risk_summary():
    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                COUNT(*) FILTER (
                    WHERE churn_probability >= 0.70
                ) AS high_risk_customers,

                COUNT(*) FILTER (
                    WHERE churn_probability >= 0.40
                    AND churn_probability < 0.70
                ) AS medium_risk_customers,

                COUNT(*) FILTER (
                    WHERE churn_probability < 0.40
                ) AS low_risk_customers,

                COUNT(*) FILTER (
                    WHERE churn_probability IS NOT NULL
                ) AS customers_with_predictions

            FROM customer_churn;
        """)

        with engine.connect() as connection:
            result = connection.execute(query)
            row = result.mappings().first()

        return dict(row)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )