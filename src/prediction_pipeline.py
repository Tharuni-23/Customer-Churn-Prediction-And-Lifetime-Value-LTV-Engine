import joblib
import pandas as pd
import xgboost as xgb

from . import database as db
from preprocessing import transform


# ============================================================
# MODEL FILES
# ============================================================

PREPROCESSING_PACKAGE = "preprocessing_package.pkl"
CHURN_MODEL = "xgboost_model.json"
LTV_MODEL = "ltv_model.json"


# ============================================================
# LOAD MODELS
# ============================================================

def load_models():
    package = joblib.load(PREPROCESSING_PACKAGE)

    churn_model = xgb.XGBClassifier()
    churn_model.load_model(CHURN_MODEL)

    ltv_model = xgb.XGBRegressor()
    ltv_model.load_model(LTV_MODEL)

    return package, churn_model, ltv_model


# ============================================================
# PREDICT ONE CUSTOMER
# ============================================================

def predict_customer(customer_id):

    package, churn_model, ltv_model = load_models()

    # Get customer from PostgreSQL
    customer = db.get_customer(customer_id)

    if customer is None:
        raise ValueError(
            f"Customer not found: {customer_id}"
        )

    # Convert customer dictionary to DataFrame
    df = pd.DataFrame([customer])

    # Preprocess customer data
    X = transform(df, package)

    # --------------------------------------------------------
    # CHURN PREDICTION
    # --------------------------------------------------------

    churn_probability = float(
        churn_model.predict_proba(X)[0, 1]
    )

    predicted_churn = (
        "Yes"
        if churn_probability >= 0.50
        else "No"
    )

    # --------------------------------------------------------
    # LTV PREDICTION
    # --------------------------------------------------------

    predicted_ltv = float(
        ltv_model.predict(X)[0]
    )

    # --------------------------------------------------------
    # SAVE PREDICTION TO DATABASE
    # --------------------------------------------------------

    db.write_prediction(
        customer_id,
        predicted_churn,
        churn_probability,
        predicted_ltv
    )

    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {
        "customerID": customer_id,
        "predicted_churn": predicted_churn,
        "churn_probability": churn_probability,
        "predicted_ltv": predicted_ltv
    }


