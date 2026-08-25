import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
from datetime import datetime

import database as db
import preprocessing


# ============================================================
# FILES
# ============================================================

PREPROCESSING_PACKAGE_PATH = (
    "preprocessing_package.pkl"
)

CHURN_MODEL_PATH = (
    "xgboost_model.json"
)

LTV_MODEL_PATH = (
    "ltv_model.json"
)


# ============================================================
# ONE PIPELINE RUN
# ============================================================

def run_pipeline():

    print("\n" + "=" * 70)
    print("STARTING CHURN + LTV PIPELINE")
    print("=" * 70)


    # --------------------------------------------------------
    # 1. CONNECT
    # --------------------------------------------------------

    engine = db.get_engine()

    db.test_connection(
        engine
    )


    # --------------------------------------------------------
    # 2. FETCH PENDING ROWS
    # --------------------------------------------------------

    raw_df = (
        db.fetch_pending_customers(
            engine
        )
    )

    if raw_df.empty:

        print(
            "No new or updated customers "
            "require prediction."
        )

        return


    print(
        f"Rows to process: {len(raw_df)}"
    )


    # --------------------------------------------------------
    # 3. LOAD PREPROCESSING PACKAGE
    # --------------------------------------------------------

    package = joblib.load(
        PREPROCESSING_PACKAGE_PATH
    )

    print(
        "Preprocessing package loaded."
    )


    # --------------------------------------------------------
    # 4. PREPROCESS
    # --------------------------------------------------------

    features_df = (
        preprocessing.transform(
            raw_df,
            package
        )
    )

    print(
        "Processed shape:",
        features_df.shape
    )


    # --------------------------------------------------------
    # 5. VALIDATE FEATURES
    # --------------------------------------------------------

    expected_features = len(
        package["feature_order"]
    )

    actual_features = (
        features_df.shape[1]
    )

    if actual_features != expected_features:

        raise ValueError(
            f"Feature mismatch: "
            f"expected {expected_features}, "
            f"got {actual_features}"
        )


    if features_df.isnull().sum().sum() > 0:

        raise ValueError(
            "NaN detected after preprocessing."
        )


    X_input = (
        features_df
        .to_numpy(
            dtype=np.float32
        )
    )


    # --------------------------------------------------------
    # 6. LOAD CHURN MODEL
    # --------------------------------------------------------

    churn_model = (
        xgb.XGBClassifier()
    )

    churn_model.load_model(
        CHURN_MODEL_PATH
    )

    print(
        "Churn model loaded."
    )


    # --------------------------------------------------------
    # 7. CHURN PREDICTION
    # --------------------------------------------------------

    churn_probability = (
        churn_model
        .predict_proba(
            X_input
        )[:, 1]
    )

    threshold = 0.50

    churn_prediction = (
        churn_probability >= threshold
    ).astype(int)


    # --------------------------------------------------------
    # 8. LOAD LTV MODEL
    # --------------------------------------------------------

    ltv_model = (
        xgb.XGBRegressor()
    )

    ltv_model.load_model(
        LTV_MODEL_PATH
    )

    print(
        "LTV model loaded."
    )


    # --------------------------------------------------------
    # 9. LTV PREDICTION
    # --------------------------------------------------------

    predicted_ltv = (
        ltv_model.predict(
            X_input
        )
    )


    # --------------------------------------------------------
    # 10. CREATE RESULT
    # --------------------------------------------------------

    customer_id_col = next(
        (
            col
            for col in raw_df.columns
            if col.lower() ==
               "customerid"
        ),
        None
    )

    if customer_id_col is None:

        raise ValueError(
            "customerID not found."
        )


    result = pd.DataFrame({

        "customerid":
            raw_df[
                customer_id_col
            ].values,

        "churn":
            np.where(
                churn_prediction == 1,
                "Yes",
                "No"
            ),

        "churn_probability":
            churn_probability,

        "predicted_ltv":
            predicted_ltv
    })


    # --------------------------------------------------------
    # 11. SHOW MODEL OUTPUT
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("MODEL OUTPUT")
    print("=" * 70)

    print(
        result.to_string(
            index=False
        )
    )


    # --------------------------------------------------------
    # 12. WRITE PREDICTIONS
    # --------------------------------------------------------

    db.write_predictions(
        result,
        engine
    )


    # --------------------------------------------------------
    # 13. ONLY AFTER SUCCESSFUL WRITE:
    #    UPDATE CHECKPOINT
    # --------------------------------------------------------

    checkpoint_time = (
        datetime.now()
    )

    db.update_checkpoint(
        checkpoint_time,
        engine
    )


    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED")
    print("=" * 70)


if __name__ == "__main__":

    run_pipeline()