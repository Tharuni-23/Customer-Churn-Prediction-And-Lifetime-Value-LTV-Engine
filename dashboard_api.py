from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

import database as db


app = FastAPI(
    title="Customer Churn & LTV Manager Dashboard API",
    version="2.1.0",
    description="Manager dashboard API backed by Neon PostgreSQL."
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Customer Churn & LTV Manager Dashboard API"
    }


# =========================================================
# SUMMARY
# =========================================================

@app.get("/dashboard/summary")
def dashboard_summary():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                COUNT(*) AS total_customers,

                COUNT(*) FILTER (
                    WHERE churn = 'Yes'
                ) AS churn_customers,

                COUNT(*) FILTER (
                    WHERE churn = 'No'
                ) AS retained_customers,

                COUNT(*) FILTER (
                    WHERE churn_probability >= 0.70
                ) AS high_risk_customers,

                COUNT(*) FILTER (
                    WHERE churn_probability >= 0.70
                      AND predicted_ltv >= 5000
                ) AS high_risk_high_ltv_customers,

                AVG(churn_probability) AS avg_churn_probability,

                AVG(predicted_ltv) AS avg_predicted_ltv,

                SUM(predicted_ltv) AS total_predicted_ltv,

                AVG(monthlycharges) AS avg_monthly_charges

            FROM public.customers
        """)

        with engine.connect() as connection:
            row = connection.execute(query).mappings().first()

        if row is None:
            return {
                "total_customers": 0,
                "churn_customers": 0,
                "retained_customers": 0,
                "churn_rate": 0,
                "high_risk_customers": 0,
                "high_risk_high_ltv_customers": 0,
                "avg_churn_probability": 0,
                "avg_predicted_ltv": 0,
                "total_predicted_ltv": 0,
                "avg_monthly_charges": 0
            }

        total = int(row["total_customers"] or 0)
        churn = int(row["churn_customers"] or 0)

        churn_rate = churn / total if total > 0 else 0

        return {
            "total_customers": total,
            "churn_customers": churn,
            "retained_customers": int(row["retained_customers"] or 0),
            "churn_rate": churn_rate,
            "high_risk_customers": int(row["high_risk_customers"] or 0),
            "high_risk_high_ltv_customers": int(
                row["high_risk_high_ltv_customers"] or 0
            ),
            "avg_churn_probability": float(
                row["avg_churn_probability"] or 0
            ),
            "avg_predicted_ltv": float(
                row["avg_predicted_ltv"] or 0
            ),
            "total_predicted_ltv": float(
                row["total_predicted_ltv"] or 0
            ),
            "avg_monthly_charges": float(
                row["avg_monthly_charges"] or 0
            )
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load dashboard summary: {str(e)}"
        )


# =========================================================
# RECENT CUSTOMERS
# =========================================================

@app.get("/dashboard/customers")
def dashboard_customers():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                customerid,
                gender,
                seniorcitizen,
                partner,
                dependents,
                tenure,
                phoneservice,
                multiplelines,
                internetservice,
                onlinesecurity,
                onlinebackup,
                deviceprotection,
                techsupport,
                streamingtv,
                streamingmovies,
                contract,
                paperlessbilling,
                paymentmethod,
                monthlycharges,
                totalcharges,
                churn,
                tenuregroup,
                totalservices,
                churn_probability,
                predicted_ltv,
                prediction_at

            FROM public.customers

            WHERE churn IS NOT NULL

            ORDER BY
                prediction_at DESC NULLS LAST,
                customerid

            LIMIT 100
        """)

        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        return {
            "customers": [dict(row) for row in rows]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load customers: {str(e)}"
        )


# =========================================================
# SINGLE CUSTOMER DETAILS
# =========================================================

@app.get("/dashboard/customer/{customerid}")
def dashboard_customer(customerid: str):

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                customerid,
                gender,
                seniorcitizen,
                partner,
                dependents,
                tenure,
                phoneservice,
                multiplelines,
                internetservice,
                onlinesecurity,
                onlinebackup,
                deviceprotection,
                techsupport,
                streamingtv,
                streamingmovies,
                contract,
                paperlessbilling,
                paymentmethod,
                monthlycharges,
                totalcharges,
                churn,
                tenuregroup,
                totalservices,
                churn_probability,
                predicted_ltv,
                prediction_at

            FROM public.customers

            WHERE customerid = :customerid

            LIMIT 1
        """)

        with engine.connect() as connection:
            row = connection.execute(
                query,
                {"customerid": customerid}
            ).mappings().first()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Customer '{customerid}' not found"
            )

        return {
            "customer": dict(row)
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load customer: {str(e)}"
        )


# =========================================================
# GLOBAL CHURN RISK
# =========================================================

@app.get("/dashboard/churn-risk")
def dashboard_churn_risk():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                CASE
                    WHEN churn_probability < 0.30
                        THEN 'Low Risk'
                    WHEN churn_probability < 0.70
                        THEN 'Medium Risk'
                    ELSE 'High Risk'
                END AS risk_level,

                COUNT(*) AS customer_count

            FROM public.customers

            WHERE churn_probability IS NOT NULL

            GROUP BY
                CASE
                    WHEN churn_probability < 0.30
                        THEN 'Low Risk'
                    WHEN churn_probability < 0.70
                        THEN 'Medium Risk'
                    ELSE 'High Risk'
                END

            ORDER BY
                MIN(churn_probability)
        """)

        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        return {
            "risk_distribution": [dict(row) for row in rows]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load churn risk data: {str(e)}"
        )


# =========================================================
# LTV SEGMENTATION
# =========================================================

@app.get("/dashboard/ltv-segments")
def dashboard_ltv_segments():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                CASE
                    WHEN predicted_ltv < 2000
                        THEN 'Low LTV'
                    WHEN predicted_ltv < 5000
                        THEN 'Medium LTV'
                    ELSE 'High LTV'
                END AS ltv_segment,

                COUNT(*) AS customer_count,

                AVG(predicted_ltv) AS average_ltv

            FROM public.customers

            WHERE predicted_ltv IS NOT NULL

            GROUP BY
                CASE
                    WHEN predicted_ltv < 2000
                        THEN 'Low LTV'
                    WHEN predicted_ltv < 5000
                        THEN 'Medium LTV'
                    ELSE 'High LTV'
                END

            ORDER BY
                MIN(predicted_ltv)
        """)

        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        return {
            "ltv_segments": [dict(row) for row in rows]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load LTV segmentation: {str(e)}"
        )


# =========================================================
# PRIORITY CUSTOMERS
# =========================================================

@app.get("/dashboard/priority-customers")
def dashboard_priority_customers():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                customerid,
                churn,
                churn_probability,
                predicted_ltv,
                contract,
                tenure,
                monthlycharges,
                prediction_at

            FROM public.customers

            WHERE churn_probability >= 0.70
              AND predicted_ltv >= 5000

            ORDER BY
                predicted_ltv DESC,
                churn_probability DESC

            LIMIT 100
        """)

        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        return {
            "priority_customers": [dict(row) for row in rows]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load priority customers: {str(e)}"
        )


# =========================================================
# CHURN BY GENDER
# =========================================================

@app.get("/dashboard/churn-by-gender")
def churn_by_gender():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                gender,
                COUNT(*) AS total_customers,

                COUNT(*) FILTER (
                    WHERE churn = 'Yes'
                ) AS churn_customers

            FROM public.customers

            GROUP BY gender

            ORDER BY gender
        """)

        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        return {
            "data": [dict(row) for row in rows]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load gender analysis: {str(e)}"
        )


# =========================================================
# CHURN BY CONTRACT
# =========================================================

@app.get("/dashboard/churn-by-contract")
def churn_by_contract():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                contract,
                COUNT(*) AS total_customers,

                COUNT(*) FILTER (
                    WHERE churn = 'Yes'
                ) AS churn_customers

            FROM public.customers

            GROUP BY contract

            ORDER BY contract
        """)

        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        return {
            "data": [dict(row) for row in rows]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load contract analysis: {str(e)}"
        )


# =========================================================
# CHURN BY INTERNET SERVICE
# =========================================================

@app.get("/dashboard/churn-by-internet")
def churn_by_internet():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                internetservice AS internet_service,
                COUNT(*) AS total_customers,

                COUNT(*) FILTER (
                    WHERE churn = 'Yes'
                ) AS churn_customers

            FROM public.customers

            GROUP BY internetservice

            ORDER BY internetservice
        """)

        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        return {
            "data": [dict(row) for row in rows]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load internet service analysis: {str(e)}"
        )


# =========================================================
# CHURN BY PARTNER
# =========================================================

@app.get("/dashboard/churn-by-partner")
def churn_by_partner():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                partner,
                COUNT(*) AS total_customers,

                COUNT(*) FILTER (
                    WHERE churn = 'Yes'
                ) AS churn_customers

            FROM public.customers

            GROUP BY partner

            ORDER BY partner
        """)

        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        return {
            "data": [dict(row) for row in rows]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load partner analysis: {str(e)}"
        )


# =========================================================
# CHURN BY TENURE
# =========================================================

@app.get("/dashboard/churn-by-tenure")
def churn_by_tenure():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                CASE
                    WHEN tenure <= 12
                        THEN '0-1 Year'
                    WHEN tenure <= 24
                        THEN '1-2 Years'
                    WHEN tenure <= 48
                        THEN '2-4 Years'
                    WHEN tenure <= 72
                        THEN '4-6 Years'
                    ELSE '6+ Years'
                END AS tenure_segment,

                COUNT(*) AS total_customers,

                COUNT(*) FILTER (
                    WHERE churn = 'Yes'
                ) AS churn_customers

            FROM public.customers

            WHERE tenure IS NOT NULL

            GROUP BY
                CASE
                    WHEN tenure <= 12
                        THEN '0-1 Year'
                    WHEN tenure <= 24
                        THEN '1-2 Years'
                    WHEN tenure <= 48
                        THEN '2-4 Years'
                    WHEN tenure <= 72
                        THEN '4-6 Years'
                    ELSE '6+ Years'
                END

            ORDER BY
                MIN(tenure)
        """)

        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        return {
            "data": [dict(row) for row in rows]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load tenure analysis: {str(e)}"
        )


# =========================================================
# CHURN BY PAYMENT METHOD
# =========================================================

@app.get("/dashboard/churn-by-payment")
def churn_by_payment():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                paymentmethod AS payment_method,
                COUNT(*) AS total_customers,

                COUNT(*) FILTER (
                    WHERE churn = 'Yes'
                ) AS churn_customers

            FROM public.customers

            GROUP BY paymentmethod

            ORDER BY churn_customers DESC
        """)

        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        return {
            "data": [dict(row) for row in rows]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load payment analysis: {str(e)}"
        )


# =========================================================
# CHURN BY NUMBER OF SERVICES
# =========================================================

@app.get("/dashboard/churn-by-services")
def churn_by_services():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                totalservices AS total_services,

                COUNT(*) AS total_customers,

                COUNT(*) FILTER (
                    WHERE churn = 'Yes'
                ) AS churn_customers

            FROM public.customers

            WHERE totalservices IS NOT NULL

            GROUP BY totalservices

            ORDER BY totalservices
        """)

        with engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        return {
            "data": [dict(row) for row in rows]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load service analysis: {str(e)}"
        )