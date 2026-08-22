import os
import pandas as pd

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_engine():

    db_user = os.environ.get(
        "DB_USER",
        "postgres"
    )

    db_password = os.environ[
        "DB_PASSWORD"
    ]

    db_host = os.environ.get(
        "DB_HOST",
        "::1"
    )

    db_port = os.environ.get(
        "DB_PORT",
        "5432"
    )

    db_name = os.environ.get(
        "DB_NAME",
        "telco_churn"
    )

    return create_engine(
        f"postgresql+psycopg2://"
        f"{db_user}:{db_password}@"
        f"[{db_host}]:{db_port}/{db_name}"
    )


# ============================================================
# TEST CONNECTION
# ============================================================

def test_connection(engine=None):

    if engine is None:
        engine = get_engine()

    with engine.connect():
        print(
            "PostgreSQL connected successfully!"
        )

    return True


# ============================================================
# FETCH PENDING CUSTOMERS
# ============================================================

def fetch_pending_customers(
    engine=None
):

    if engine is None:
        engine = get_engine()

    query = """
        SELECT *
        FROM public.customers
        WHERE updated_at > COALESCE(
            (
                SELECT last_successful_run
                FROM pipeline_checkpoint
                WHERE pipeline_name =
                    'churn_ltv_pipeline'
            ),
            TIMESTAMP '1970-01-01'
        )
        AND churn IS NULL
        ORDER BY updated_at;
    """

    df = pd.read_sql(
        query,
        engine
    )

    print(
        f"Fetched {len(df)} pending customers."
    )

    return df


# ============================================================
# MARK PREDICTIONS COMPLETE
# ============================================================

def write_predictions(
    result,
    engine=None
):

    if engine is None:
        engine = get_engine()

    if result.empty:
        return

    sql = text("""
        UPDATE public.customers
        SET
            churn = :churn,
            churn_probability = :churn_probability,
            predicted_ltv = :predicted_ltv,
            prediction_at = CURRENT_TIMESTAMP
        WHERE customerid = :customerid
    """)

    records = result[
        [
            "customerid",
            "churn",
            "churn_probability",
            "predicted_ltv"
        ]
    ].to_dict(
        orient="records"
    )

    with engine.begin() as connection:

        connection.execute(
            sql,
            records
        )

    print(
        f"Updated {len(records)} customers "
        "with predictions."
    )


# ============================================================
# UPDATE CHECKPOINT
# ============================================================

def update_checkpoint(
    run_time,
    engine=None
):

    if engine is None:
        engine = get_engine()

    sql = text("""
        UPDATE pipeline_checkpoint
        SET last_successful_run = :run_time
        WHERE pipeline_name =
            'churn_ltv_pipeline'
    """)

    with engine.begin() as connection:

        connection.execute(
            sql,
            {
                "run_time": run_time
            }
        )

    print(
        "Pipeline checkpoint updated:",
        run_time
    )