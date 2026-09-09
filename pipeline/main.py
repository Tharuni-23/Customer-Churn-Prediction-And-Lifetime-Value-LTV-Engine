# ============================================================
# pipeline/main.py
#
# CUSTOMER CHURN + LTV PREDICTION PIPELINE
# ============================================================

import pandas as pd
import numpy as np
import joblib
import xgboost as xgb

from pipeline import database as db
from pipeline import change_tracker
from preprocessing import preprocessing


# ============================================================
# FILE PATHS
# ============================================================

PREPROCESSING_PACKAGE_PATH = "preprocessing/preprocessing_package.pkl"
CHURN_MODEL_PATH = "models/xgboost_model.json"
LTV_MODEL_PATH = "models/ltv_model.json"


# ============================================================
# ONE PIPELINE RUN
# ============================================================

def run_pipeline():

    print()
    print("=" * 70)
    print("STARTING CHURN + LTV PIPELINE")
    print("=" * 70)

    # --------------------------------------------------------
    # Connect to Neon PostgreSQL
    # --------------------------------------------------------

    print("\nConnecting to Neon PostgreSQL...")

    engine = db.get_engine()
    db.test_connection(engine)

    # --------------------------------------------------------
    # Processing Window
    # --------------------------------------------------------

    window_start, window_end = change_tracker.create_processing_window()
    run_time = window_end

    change_tracker.print_processing_window(
        window_start,
        window_end
    )

    # --------------------------------------------------------
    # Fetch Updated Customers
    # --------------------------------------------------------

    print("\nChecking for new or updated customers...")

    raw_df = db.fetch_customers_in_window(
        window_start,
        window_end,
        engine
    )

    if raw_df.empty:

        print("\nNo new or updated customers require prediction.")

        change_tracker.save_last_successful_run(run_time)

        print(
            "Processing window checkpoint updated:",
            run_time
        )

        return

    print(f"\nRows to process: {len(raw_df)}")

    # --------------------------------------------------------
    # Load Preprocessing Package
    # --------------------------------------------------------

    print("\nLoading preprocessing package...")

    package = joblib.load(PREPROCESSING_PACKAGE_PATH)

    print("Preprocessing package loaded.")

    # --------------------------------------------------------
    # Transform Features
    # --------------------------------------------------------

    print("\nPreprocessing incoming customer data...")

    features_df = preprocessing.transform(
        raw_df,
        package
    )

    expected_features = len(package["feature_order"])
    actual_features = features_df.shape[1]

    if actual_features != expected_features:
        raise ValueError(
            f"Feature mismatch: expected {expected_features}, got {actual_features}"
        )

    if features_df.isnull().sum().sum() > 0:
        raise ValueError("NaN detected after preprocessing.")

    X_input = features_df.to_numpy(dtype=np.float32)

    print("Feature matrix ready:", X_input.shape)

    # --------------------------------------------------------
    # Churn Model
    # --------------------------------------------------------

    print("\nLoading churn model...")

    churn_model = xgb.XGBClassifier()
    churn_model.load_model(CHURN_MODEL_PATH)

    churn_probability = churn_model.predict_proba(X_input)[:, 1]
    churn_prediction = (churn_probability >= 0.50).astype(int)

    # --------------------------------------------------------
    # LTV Model
    # --------------------------------------------------------

    print("\nLoading LTV model...")

    ltv_model = xgb.XGBRegressor()
    ltv_model.load_model(LTV_MODEL_PATH)

    predicted_ltv = ltv_model.predict(X_input)

    # --------------------------------------------------------
    # Result DataFrame
    # --------------------------------------------------------

    customer_id_col = next(
        (c for c in raw_df.columns if c.lower() == "customerid"),
        None
    )

    if customer_id_col is None:
        raise ValueError("customerID column not found.")

    result = pd.DataFrame({
        "customerid": raw_df[customer_id_col].values,
        "churn": np.where(churn_prediction == 1, "Yes", "No"),
        "churn_probability": churn_probability,
        "predicted_ltv": predicted_ltv
    })

    print("\nMODEL OUTPUT")
    print(result.to_string(index=False))

    # --------------------------------------------------------
    # Save Predictions
    # --------------------------------------------------------

    print("\nWriting predictions to Neon PostgreSQL...")

    db.write_predictions(result, engine)

    change_tracker.save_last_successful_run(run_time)

    print(
        "Processing window checkpoint updated:",
        run_time
    )

    print("\nPIPELINE COMPLETED SUCCESSFULLY")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_pipeline()