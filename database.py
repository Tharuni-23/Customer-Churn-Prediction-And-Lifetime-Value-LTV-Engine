import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


def get_engine():
    db_user = os.environ.get("DB_USER", "postgres")
    db_password = os.environ["DB_PASSWORD"]
    db_host = os.environ.get("DB_HOST", "::1")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME", "telco_churn")

    return create_engine(
        f"postgresql+psycopg2://{db_user}:{db_password}@[{db_host}]:{db_port}/{db_name}"
    )


def test_connection(engine=None):
    if engine is None:
        engine = get_engine()

    try:
        with engine.connect():
            print("PostgreSQL connected successfully!")
        return True

    except Exception as e:
        print("Connection failed:")
        print(e)
        raise


def fetch_all_customers(engine=None):
    if engine is None:
        engine = get_engine()

    query = """
    SELECT *
    FROM public.customers
    """

    raw_df = pd.read_sql(query, engine)

    print(
        f"Fetched {len(raw_df)} rows, "
        f"{raw_df.shape[1]} columns."
    )

    return raw_df


def fetch_recently_updated_customers(engine=None):
    if engine is None:
        engine = get_engine()

    query = """
    SELECT *
    FROM public.customers
    WHERE updated_at >= CURRENT_TIMESTAMP - INTERVAL '5 minutes'
    ORDER BY updated_at
    """

    raw_df = pd.read_sql(query, engine)

    print(
        f"Fetched {len(raw_df)} recently updated rows, "
        f"{raw_df.shape[1]} columns."
    )

    return raw_df


def fetch_customer_by_id(
    customer_id,
    engine=None,
    id_column="customerid"
):
    if engine is None:
        engine = get_engine()

    query = f"""
    SELECT *
    FROM public.customers
    WHERE {id_column} = %(customer_id)s
    """

    raw_df = pd.read_sql(
        query,
        engine,
        params={"customer_id": customer_id}
    )

    if raw_df.empty:
        raise ValueError(
            f"No customer found with "
            f"{id_column} = {customer_id!r}"
        )

    print(
        f"Fetched customer {customer_id!r}."
    )

    return raw_df


if __name__ == "__main__":

    eng = get_engine()

    test_connection(eng)

    df = fetch_recently_updated_customers(
        eng
    )

    print(df.head())