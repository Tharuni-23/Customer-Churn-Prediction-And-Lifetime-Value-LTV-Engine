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

    database=os.getenv("DB_NAME")

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

        print(
            "Connected to:",
            database_name
        )


# ============================================================
# GET ALL CUSTOMERS
# ============================================================

def get_all_customers():

    query = """
        SELECT *
        FROM customer_churn
        ORDER BY "customerID";
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
def write_prediction(
    customer_id,
    predicted_churn,
    churn_probability,
    predicted_ltv
):
    query = text("""
        UPDATE customer_churn
        SET
            predicted_churn = :predicted_churn,
            churn_probability = :churn_probability,
            predicted_ltv = :predicted_ltv,
            prediction_at = CURRENT_TIMESTAMP
        WHERE "customerID" = :customer_id;
    """)

    with engine.connect() as connection:
        connection.execute(
            query,
            {
                "customer_id": customer_id,
                "predicted_churn": predicted_churn,
                "churn_probability": churn_probability,
                "predicted_ltv": predicted_ltv
            }
        )
        connection.commit()