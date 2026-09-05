# ============================================================
# test_api.py
#
# PURPOSE
# ------------------------------------------------------------
# FastAPI backend for:
#   1. Batch test-data generation
#   2. Real-time single-customer prediction
#
# The single-customer endpoint uses the SAME:
#   - preprocessing package
#   - XGBoost churn model
#   - XGBoost LTV model
#
# After prediction, the customer and prediction are stored in
# Neon PostgreSQL so the manager dashboard can read the result.
# ============================================================

from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import database as db
import preprocessing
import test_data_generator


# ============================================================
# FILE PATHS
# ============================================================

PREPROCESSING_PACKAGE_PATH = "preprocessing_package.pkl"
CHURN_MODEL_PATH = "xgboost_model.json"
LTV_MODEL_PATH = "ltv_model.json"


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Customer Churn + LTV Test API",
    description=(
        "Batch test-data generation and single-customer "
        "real-time prediction API."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SINGLE CUSTOMER REQUEST MODEL
# ============================================================

class SingleCustomerRequest(BaseModel):
    customerID: str

    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str

    tenure: int

    PhoneService: str
    MultipleLines: str

    InternetService: str

    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str

    Contract: str
    PaperlessBilling: str
    PaymentMethod: str

    MonthlyCharges: float
    TotalCharges: float

    TotalServices: int


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root() -> Dict[str, str]:
    return {
        "status": "running",
        "service": "Customer Churn + LTV Test API",
    }


@app.get("/health")
def health() -> Dict[str, str]:
    try:
        engine = db.get_engine()

        with engine.connect():
            pass

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as exc:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(exc),
        }


# ============================================================
# BATCH TEST DATA
# ============================================================

@app.post("/generate-test-data")
def generate_test_data() -> Dict[str, Any]:

    try:
        result = (
            test_data_generator
            .generate_test_data()
        )

        return {
            "success": True,
            "updated": len(
                result["updated"]
            ),
            "inserted": len(
                result["inserted"]
            ),
            "total": (
                len(result["updated"])
                +
                len(result["inserted"])
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# TENURE GROUP
# ============================================================

def get_tenure_group(tenure: int) -> str:

    if tenure <= 12:
        return "0-1 Year"

    if tenure <= 24:
        return "1-2 Years"

    if tenure <= 48:
        return "2-4 Years"

    return "4-6 Years"


# ============================================================
# UPSERT CUSTOMER INTO DATABASE
# ============================================================

def save_single_customer(
    payload: Dict[str, Any],
    engine=None,
) -> None:

    if engine is None:
        engine = db.get_engine()

    from sqlalchemy import text

    sql = text(
        """
        INSERT INTO public.customers (
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
            prediction_at,
            updated_at
        )
        VALUES (
            :customerid,
            :gender,
            :seniorcitizen,
            :partner,
            :dependents,
            :tenure,
            :phoneservice,
            :multiplelines,
            :internetservice,
            :onlinesecurity,
            :onlinebackup,
            :deviceprotection,
            :techsupport,
            :streamingtv,
            :streamingmovies,
            :contract,
            :paperlessbilling,
            :paymentmethod,
            :monthlycharges,
            :totalcharges,
            NULL,
            :tenuregroup,
            :totalservices,
            NULL,
            NULL,
            NULL,
            CURRENT_TIMESTAMP
        )
        ON CONFLICT (customerid)
        DO UPDATE SET
            gender = EXCLUDED.gender,
            seniorcitizen = EXCLUDED.seniorcitizen,
            partner = EXCLUDED.partner,
            dependents = EXCLUDED.dependents,
            tenure = EXCLUDED.tenure,
            phoneservice = EXCLUDED.phoneservice,
            multiplelines = EXCLUDED.multiplelines,
            internetservice = EXCLUDED.internetservice,
            onlinesecurity = EXCLUDED.onlinesecurity,
            onlinebackup = EXCLUDED.onlinebackup,
            deviceprotection = EXCLUDED.deviceprotection,
            techsupport = EXCLUDED.techsupport,
            streamingtv = EXCLUDED.streamingtv,
            streamingmovies = EXCLUDED.streamingmovies,
            contract = EXCLUDED.contract,
            paperlessbilling = EXCLUDED.paperlessbilling,
            paymentmethod = EXCLUDED.paymentmethod,
            monthlycharges = EXCLUDED.monthlycharges,
            totalcharges = EXCLUDED.totalcharges,
            churn = NULL,
            tenuregroup = EXCLUDED.tenuregroup,
            totalservices = EXCLUDED.totalservices,
            churn_probability = NULL,
            predicted_ltv = NULL,
            prediction_at = NULL,
            updated_at = CURRENT_TIMESTAMP
        """
    )

    with engine.begin() as connection:
        connection.execute(
            sql,
            payload,
        )


# ============================================================
# WRITE SINGLE CUSTOMER PREDICTION
# ============================================================

def save_prediction(
    customer_id: str,
    churn_prediction: str,
    churn_probability: float,
    predicted_ltv: float,
    engine=None,
) -> None:

    if engine is None:
        engine = db.get_engine()

    from sqlalchemy import text

    sql = text(
        """
        UPDATE public.customers
        SET
            churn = :churn,
            churn_probability = :churn_probability,
            predicted_ltv = :predicted_ltv,
            prediction_at = CURRENT_TIMESTAMP
        WHERE customerid = :customerid
        """
    )

    with engine.begin() as connection:
        connection.execute(
            sql,
            {
                "customerid": customer_id,
                "churn": churn_prediction,
                "churn_probability": churn_probability,
                "predicted_ltv": predicted_ltv,
            },
        )


# ============================================================
# SINGLE CUSTOMER PREDICTION
# ============================================================

@app.post("/predict-single-customer")
def predict_single_customer(
    request: SingleCustomerRequest,
) -> Dict[str, Any]:

    try:
        # --------------------------------------------------------
        # 1. Convert request into canonical raw customer row
        # --------------------------------------------------------

        raw_data = request.model_dump()

        raw_data["TenureGroup"] = get_tenure_group(
            int(request.tenure)
        )

        raw_data["Churn"] = None

        raw_df = pd.DataFrame(
            [raw_data]
        )

        # --------------------------------------------------------
        # 2. Connect to database
        # --------------------------------------------------------

        engine = db.get_engine()

        # --------------------------------------------------------
        # 3. Store customer first
        #
        # This makes the new customer visible to the dashboard.
        # Prediction fields are then filled immediately below.
        # --------------------------------------------------------

        database_payload = {
            "customerid": raw_data["customerID"],
            "gender": raw_data["gender"],
            "seniorcitizen": raw_data["SeniorCitizen"],
            "partner": raw_data["Partner"],
            "dependents": raw_data["Dependents"],
            "tenure": raw_data["tenure"],
            "phoneservice": raw_data["PhoneService"],
            "multiplelines": raw_data["MultipleLines"],
            "internetservice": raw_data["InternetService"],
            "onlinesecurity": raw_data["OnlineSecurity"],
            "onlinebackup": raw_data["OnlineBackup"],
            "deviceprotection": raw_data["DeviceProtection"],
            "techsupport": raw_data["TechSupport"],
            "streamingtv": raw_data["StreamingTV"],
            "streamingmovies": raw_data["StreamingMovies"],
            "contract": raw_data["Contract"],
            "paperlessbilling": raw_data["PaperlessBilling"],
            "paymentmethod": raw_data["PaymentMethod"],
            "monthlycharges": raw_data["MonthlyCharges"],
            "totalcharges": raw_data["TotalCharges"],
            "tenuregroup": raw_data["TenureGroup"],
            "totalservices": raw_data["TotalServices"],
        }

        save_single_customer(
            database_payload,
            engine,
        )

        # --------------------------------------------------------
        # 4. Load the SAME preprocessing package used by pipeline
        # --------------------------------------------------------

        package = joblib.load(
            PREPROCESSING_PACKAGE_PATH
        )

        # --------------------------------------------------------
        # 5. Transform raw customer data
        # --------------------------------------------------------

        features_df = preprocessing.transform(
            raw_df,
            package,
        )

        # --------------------------------------------------------
        # 6. Convert to model input
        # --------------------------------------------------------

        X_input = features_df.to_numpy(
            dtype=np.float32
        )

        expected_features = len(
            package["feature_order"]
        )

        if X_input.shape[1] != expected_features:
            raise ValueError(
                "Feature mismatch: "
                f"expected {expected_features}, "
                f"got {X_input.shape[1]}"
            )

        # --------------------------------------------------------
        # 7. Load churn model
        # --------------------------------------------------------

        churn_model = xgb.XGBClassifier()

        churn_model.load_model(
            CHURN_MODEL_PATH
        )

        # --------------------------------------------------------
        # 8. Churn prediction
        # --------------------------------------------------------

        churn_probability = float(
            churn_model
            .predict_proba(
                X_input
            )[0, 1]
        )

        churn_prediction = (
            "Yes"
            if churn_probability >= 0.50
            else "No"
        )

        # --------------------------------------------------------
        # 9. Load LTV model
        # --------------------------------------------------------

        ltv_model = xgb.XGBRegressor()

        ltv_model.load_model(
            LTV_MODEL_PATH
        )

        # --------------------------------------------------------
        # 10. LTV prediction
        # --------------------------------------------------------

        predicted_ltv = float(
            ltv_model
            .predict(
                X_input
            )[0]
        )

        # --------------------------------------------------------
        # 11. Store prediction
        # --------------------------------------------------------

        save_prediction(
            customer_id=request.customerID,
            churn_prediction=churn_prediction,
            churn_probability=churn_probability,
            predicted_ltv=predicted_ltv,
            engine=engine,
        )

        # --------------------------------------------------------
        # 12. Return result
        # --------------------------------------------------------

        if churn_probability >= 0.70:
            risk_level = "High"
        elif churn_probability >= 0.40:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return {
            "success": True,
            "customerid": request.customerID,
            "churn": churn_prediction,
            "churn_probability": round(
                churn_probability,
                6,
            ),
            "predicted_ltv": round(
                predicted_ltv,
                2,
            ),
            "risk_level": risk_level,
            "saved_to_database": True,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
