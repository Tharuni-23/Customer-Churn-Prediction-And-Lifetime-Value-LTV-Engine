# ============================================================
# test_api.py
#
# PURPOSE
# ------------------------------------------------------------
# FastAPI backend for:
#   1. Batch test-data generation
#   2. Single-customer real-time prediction
#
# SINGLE-CUSTOMER FLOW
# ------------------------------------------------------------
# Frontend
#     ↓
# FastAPI
#     ↓
# Same preprocessing package
#     ↓
# XGBoost Churn Model + XGBoost LTV Model
#     ↓
# Neon PostgreSQL
#
# The single-customer endpoint uses the same model artifacts
# already used by the integrated prediction pipeline.
# ============================================================

from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sqlalchemy import text

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
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Customer Churn + LTV Test API",
    description=(
        "Batch test-data generation and single-customer "
        "real-time churn and LTV prediction API."
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
# ROOT
# ============================================================

@app.get("/")
def root() -> Dict[str, str]:
    return {
        "status": "running",
        "service": "Customer Churn + LTV Test API",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health() -> Dict[str, Any]:

    try:
        engine = db.get_engine()

        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

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
# BATCH TEST DATA GENERATOR
# ============================================================

@app.post("/generate-test-data")
def generate_test_data() -> Dict[str, Any]:

    try:
        result = (
            test_data_generator
            .generate_test_data()
        )

        updated_count = len(
            result["updated"]
        )

        inserted_count = len(
            result["inserted"]
        )

        return {
            "success": True,
            "updated": updated_count,
            "inserted": inserted_count,
            "total": (
                updated_count
                +
                inserted_count
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
# VALIDATE SINGLE CUSTOMER INPUT
# ============================================================

def validate_single_customer(
    request: SingleCustomerRequest,
) -> None:

    if not request.customerID.strip():
        raise HTTPException(
            status_code=400,
            detail="Customer ID cannot be empty.",
        )

    if request.tenure < 0 or request.tenure > 72:
        raise HTTPException(
            status_code=400,
            detail="Tenure must be between 0 and 72 months.",
        )

    if request.SeniorCitizen not in (0, 1):
        raise HTTPException(
            status_code=400,
            detail="SeniorCitizen must be 0 or 1.",
        )

    if request.MonthlyCharges < 0:
        raise HTTPException(
            status_code=400,
            detail="Monthly charges cannot be negative.",
        )

    if request.TotalCharges < 0:
        raise HTTPException(
            status_code=400,
            detail="Total charges cannot be negative.",
        )

    if request.TotalServices < 0 or request.TotalServices > 7:
        raise HTTPException(
            status_code=400,
            detail="Total services must be between 0 and 7.",
        )


# ============================================================
# SAVE SINGLE CUSTOMER
# ============================================================

def save_single_customer(
    payload: Dict[str, Any],
    engine=None,
) -> None:

    if engine is None:
        engine = db.get_engine()

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
# SAVE SINGLE CUSTOMER PREDICTION
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

    # --------------------------------------------------------
    # 1. Validate input
    # --------------------------------------------------------

    validate_single_customer(
        request
    )

    try:

        # ----------------------------------------------------
        # 2. Convert request to dictionary
        # ----------------------------------------------------

        if hasattr(request, "model_dump"):
            raw_data = request.model_dump()
        else:
            raw_data = request.dict()

        # ----------------------------------------------------
        # 3. Calculate tenure group
        # ----------------------------------------------------

        raw_data["TenureGroup"] = (
            get_tenure_group(
                request.tenure
            )
        )

        # Churn is the prediction target.
        raw_data["Churn"] = None

        raw_df = pd.DataFrame(
            [raw_data]
        )

        # ----------------------------------------------------
        # 4. Connect to Neon PostgreSQL
        # ----------------------------------------------------

        engine = db.get_engine()

        # ----------------------------------------------------
        # 5. Load the SAME preprocessing package
        # ----------------------------------------------------

        package = joblib.load(
            PREPROCESSING_PACKAGE_PATH
        )

        # ----------------------------------------------------
        # 6. Transform customer input
        # ----------------------------------------------------

        features_df = preprocessing.transform(
            raw_df,
            package,
        )

        # ----------------------------------------------------
        # 7. Validate model feature count
        # ----------------------------------------------------

        expected_features = len(
            package["feature_order"]
        )

        X_input = features_df.to_numpy(
            dtype=np.float32
        )

        if X_input.shape[1] != expected_features:
            raise ValueError(
                "Feature mismatch: "
                f"expected {expected_features}, "
                f"got {X_input.shape[1]}"
            )

        # ----------------------------------------------------
        # 8. Load churn model
        # ----------------------------------------------------

        churn_model = xgb.XGBClassifier()

        churn_model.load_model(
            CHURN_MODEL_PATH
        )

        # ----------------------------------------------------
        # 9. Predict churn probability
        # ----------------------------------------------------

        churn_probability = float(
            churn_model
            .predict_proba(
                X_input
            )[0, 1]
        )

        # ----------------------------------------------------
        # 10. Convert probability to churn classification
        # ----------------------------------------------------

        churn_prediction = (
            "Yes"
            if churn_probability >= 0.50
            else "No"
        )

        # ----------------------------------------------------
        # 11. Load LTV model
        # ----------------------------------------------------

        ltv_model = xgb.XGBRegressor()

        ltv_model.load_model(
            LTV_MODEL_PATH
        )

        # ----------------------------------------------------
        # 12. Predict LTV
        # ----------------------------------------------------

        predicted_ltv = float(
            ltv_model
            .predict(
                X_input
            )[0]
        )

        # ----------------------------------------------------
        # 13. Determine risk level
        # ----------------------------------------------------

        if churn_probability >= 0.70:

            risk_level = "High"

        elif churn_probability >= 0.40:

            risk_level = "Medium"

        else:

            risk_level = "Low"

        # ----------------------------------------------------
        # 14. Save customer input to PostgreSQL
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # 15. Save prediction to PostgreSQL
        # ----------------------------------------------------

        save_prediction(
            customer_id=request.customerID,
            churn_prediction=churn_prediction,
            churn_probability=churn_probability,
            predicted_ltv=predicted_ltv,
            engine=engine,
        )

        # ----------------------------------------------------
        # 16. Return structured prediction response
        # ----------------------------------------------------

        return {
            "success": True,
            "customerid": request.customerID,
            "prediction": {
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
            },
            "saved_to_database": True,
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "test_api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )