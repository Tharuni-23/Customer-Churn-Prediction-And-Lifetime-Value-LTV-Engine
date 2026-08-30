from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import database as db


app = FastAPI(
    title="Customer Churn + LTV Dashboard API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Customer Churn + LTV Dashboard API"
    }


@app.get("/dashboard/summary")
def dashboard_summary():

    engine = db.get_engine()

    query = text("""
        SELECT
            COUNT(*) AS total_customers,
            COUNT(*) FILTER (
                WHERE churn = 'Yes'
            ) AS churn_customers,
            AVG(churn_probability) AS avg_churn_probability,
            AVG(predicted_ltv) AS avg_predicted_ltv
        FROM public.customers
    """)

    with engine.connect() as connection:
        row = connection.execute(query).mappings().first()

    return {
        "total_customers": row["total_customers"],
        "churn_customers": row["churn_customers"],
        "avg_churn_probability": float(
            row["avg_churn_probability"] or 0
        ),
        "avg_predicted_ltv": float(
            row["avg_predicted_ltv"] or 0
        )
    }


@app.get("/dashboard/customers")
def dashboard_customers():

    engine = db.get_engine()

    query = text("""
        SELECT
            customerid,
            churn,
            churn_probability,
            predicted_ltv,
            prediction_at
        FROM public.customers
        WHERE churn IS NOT NULL
        ORDER BY prediction_at DESC NULLS LAST
        LIMIT 100
    """)

    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()

    return {
        "customers": [dict(row) for row in rows]
    }