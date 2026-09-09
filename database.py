import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# DATABASE CONNECTION
# ============================================================

connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(connection_url)


# ============================================================
# GET DATABASE ENGINE
# ============================================================

def get_engine():
    return engine


# ============================================================
# TEST DATABASE CONNECTION
# ============================================================

def test_connection(engine):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database();")
        )

        database_name = result.fetchone()[0]

        print("Connected to:", database_name)


# ============================================================
# GET ALL CUSTOMERS
# ============================================================

def get_all_customers():

    query = """
        SELECT *
        FROM customers
        ORDER BY customerid;
    """

    return pd.read_sql(
        query,
        engine
    )


# ============================================================
# GET SINGLE CUSTOMER
# ============================================================

def get_customer(customer_id):

    query = text("""
        SELECT *
        FROM customers
        WHERE customerid = :customer_id;
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
            return None

        return dict(row)


# ============================================================
# GET DASHBOARD SUMMARY
# ============================================================

def get_dashboard_summary():

    query = text("""
        SELECT
            COUNT(*) AS total_customers,

            COUNT(*) FILTER (
                WHERE churn = 'Yes'
            ) AS churned_customers,

            COUNT(*) FILTER (
                WHERE churn = 'No'
            ) AS retained_customers,

            ROUND(
                AVG(monthlycharges)::numeric,
                2
            ) AS average_monthly_charges,

            ROUND(
                SUM(monthlycharges)::numeric,
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

        FROM customers;
    """)

    with engine.connect() as connection:

        result = connection.execute(query)

        row = result.mappings().first()

        return dict(row)


# ============================================================
# WRITE PREDICTION
# ============================================================

def write_prediction(
    customer_id,
    predicted_churn,
    churn_probability,
    predicted_ltv
):
    query = text("""
        UPDATE customers
        SET
            churn_probability = :churn_probability,
            predicted_ltv = :predicted_ltv,
            prediction_at = CURRENT_TIMESTAMP
        WHERE customerid = :customer_id;
    """)

    with engine.connect() as connection:
        connection.execute(
            query,
            {
                "customer_id": customer_id,
                "churn_probability": churn_probability,
                "predicted_ltv": predicted_ltv
            }
        )
        connection.commit()