from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from . import database as db


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Customer Churn & LTV API",
    description="API for Manager Dashboard",
    version="1.0.0"
)


# ============================================================
# HOME / HEALTH CHECK
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

            connection.execute(
                text("SELECT 1")
            )

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
                ) AS total_monthly_revenue

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

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from . import database as db


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Customer Churn & LTV API",
    description="API for Manager Dashboard",
    version="1.0.0"
)


# ============================================================
# HOME / HEALTH CHECK
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

            connection.execute(
                text("SELECT 1")
            )

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
                ) AS total_monthly_revenue

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
                "Mails"
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