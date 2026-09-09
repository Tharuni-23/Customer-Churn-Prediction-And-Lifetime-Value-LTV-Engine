from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import text
import numpy as np
import io

from . import database as db
from .prediction_pipeline import predict_customer

# Stores the latest uploaded CSV prediction results
# for download from the Manager Dashboard.
latest_prediction_csv = None
# ============================================================
# JSON SAFE CONVERSION
# ============================================================

def make_json_safe(value):
    """
    Convert NumPy/Pandas values into standard Python values
    that FastAPI can serialize as JSON.
    """

    if isinstance(value, dict):
        return {
            key: make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            make_json_safe(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            make_json_safe(item)
            for item in value
        ]

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    if isinstance(value, np.ndarray):
        return value.tolist()

    return value


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Customer Churn & LTV API",
    description="API for Manager Dashboard",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Customer Churn & LTV API is running"
    }


# ============================================================
# DATABASE HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    try:
        engine = db.get_engine()

        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@app.get("/dashboard/summary")
def dashboard_summary():

    try:
        engine = db.get_engine()

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
                ) AS total_monthly_revenue,

                ROUND(
                    AVG(churn_probability)::numeric,
                    4
                ) AS average_churn_probability,

                ROUND(
                    AVG(predicted_ltv)::numeric,
                    2
                ) AS average_predicted_ltv

            FROM customer_churn;
        """)

        with engine.connect() as connection:

            result = connection.execute(query)

            row = result.mappings().first()

        return dict(row)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# GET CUSTOMERS
# ============================================================

@app.get("/customers")
def get_customers():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT *
            FROM customer_churn
            ORDER BY "customerID"
            LIMIT 100;
        """)

        with engine.connect() as connection:

            result = connection.execute(query)

            customers = [
                dict(row)
                for row in result.mappings()
            ]

        return {
            "count": len(customers),
            "customers": customers
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# GET SINGLE CUSTOMER
# ============================================================

@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):

    try:
        engine = db.get_engine()

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

            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        return dict(row)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# DASHBOARD CUSTOMERS
# ============================================================

@app.get("/dashboard/customers")
def dashboard_customers():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                "customerID",
                "gender",
                "SeniorCitizen",
                "Partner",
                "Dependents",
                "tenure",
                "Contract",
                "MonthlyCharges",
                "TotalCharges",
                "Churn",
                "TenureGroup",
                "TotalServices",
                "Mails",
                predicted_churn,
                churn_probability,
                predicted_ltv,
                prediction_at

            FROM customer_churn

            ORDER BY "customerID"

            LIMIT 100;
        """)

        with engine.connect() as connection:

            result = connection.execute(query)

            customers = [
                dict(row)
                for row in result.mappings()
            ]

        return {
            "count": len(customers),
            "customers": customers
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# PREDICT CUSTOMER
# ============================================================

@app.post("/predict/{customer_id}")
def predict_customer_api(customer_id: str):

    try:

        result = predict_customer(customer_id)

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# CHURN RISK SUMMARY
# ============================================================

@app.get("/dashboard/risk-summary")
def dashboard_risk_summary():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT

                COUNT(*) FILTER (
                    WHERE churn_probability >= 0.70
                ) AS high_risk_customers,

                COUNT(*) FILTER (
                    WHERE churn_probability >= 0.40
                    AND churn_probability < 0.70
                ) AS medium_risk_customers,

                COUNT(*) FILTER (
                    WHERE churn_probability < 0.40
                ) AS low_risk_customers,

                COUNT(*) FILTER (
                    WHERE churn_probability IS NOT NULL
                ) AS customers_with_predictions

            FROM customer_churn;
        """)

        with engine.connect() as connection:

            result = connection.execute(query)

            row = result.mappings().first()

        return dict(row)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# DASHBOARD CUSTOMER DETAILS
# ============================================================

@app.get("/dashboard/customers/{customer_id}")
def dashboard_customer_details(customer_id: str):

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                "customerID",
                "gender",
                "SeniorCitizen",
                "Partner",
                "Dependents",
                "tenure",
                "Contract",
                "MonthlyCharges",
                "TotalCharges",
                "Churn",
                "TenureGroup",
                "TotalServices",
                "Mails",
                predicted_churn,
                churn_probability,
                predicted_ltv,
                prediction_at

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

            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        return dict(row)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# TOP AT-RISK CUSTOMERS
# ============================================================

@app.get("/dashboard/top-risk")
def dashboard_top_risk():

    try:
        engine = db.get_engine()

        query = text("""
            SELECT
                "customerID",
                "Contract",
                "tenure",
                "MonthlyCharges",
                predicted_churn,
                churn_probability,
                predicted_ltv,
                prediction_at

            FROM customer_churn

            WHERE churn_probability IS NOT NULL

            ORDER BY churn_probability DESC

            LIMIT 10;
        """)

        with engine.connect() as connection:

            result = connection.execute(query)

            customers = [
                dict(row)
                for row in result.mappings()
            ]

        return {
            "count": len(customers),
            "customers": customers
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# CSV UPLOAD AND PREDICTION
# ============================================================

@app.post("/dashboard/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    global latest_prediction_csv

    try:

        # ----------------------------------------------------
        # 1. Validate file
        # ----------------------------------------------------

        if not file.filename.lower().endswith(".csv"):

            raise HTTPException(
                status_code=400,
                detail="Please upload a CSV file"
            )

        # ----------------------------------------------------
        # 2. Read uploaded file
        # ----------------------------------------------------

        contents = await file.read()

        if not contents:

            raise HTTPException(
                status_code=400,
                detail="Uploaded CSV file is empty"
            )

        # ----------------------------------------------------
        # 3. Import CSV/ML tools
        # ----------------------------------------------------

        import io
        import pandas as pd

        from .prediction_pipeline import load_models
        from preprocessing import transform

        # ----------------------------------------------------
        # 4. Read CSV
        # ----------------------------------------------------

        df = pd.read_csv(
            io.BytesIO(contents)
        )

        if df.empty:

            raise HTTPException(
                status_code=400,
                detail="CSV file contains no customer records"
            )

        # ----------------------------------------------------
        # 5. Load models
        # ----------------------------------------------------

        package, churn_model, ltv_model = load_models()

        # ----------------------------------------------------
        # 6. Preserve original CSV data
        # ----------------------------------------------------

        original_df = df.copy()

        # ----------------------------------------------------
        # 7. Preprocess CSV
        # ----------------------------------------------------

        X = transform(
            df,
            package
        )

        # ----------------------------------------------------
        # 8. Churn prediction
        # ----------------------------------------------------

        churn_probabilities = (
            churn_model
            .predict_proba(X)[:, 1]
        )

        # Convert probabilities to normal Python floats
        churn_probabilities = [
            float(probability)
            for probability in churn_probabilities
        ]

        # ----------------------------------------------------
        # 9. Churn classification
        # ----------------------------------------------------

        predicted_churn = [
            "Yes"
            if probability >= 0.50
            else "No"

            for probability in churn_probabilities
        ]

        # ----------------------------------------------------
        # 10. LTV prediction
        # ----------------------------------------------------

        predicted_ltv = ltv_model.predict(X)

        predicted_ltv = [
            float(value)
            for value in predicted_ltv
        ]

        # ----------------------------------------------------
        # 11. Build dashboard results
        # ----------------------------------------------------

        # Keep only useful columns for the Manager Dashboard
        dashboard_columns = []

        for column in [
            "customerID",
            "Contract",
            "tenure",
            "MonthlyCharges"
        ]:
            if column in original_df.columns:
                dashboard_columns.append(column)

        results_df = original_df[dashboard_columns].copy()

        results_df["predicted_churn"] = predicted_churn

        results_df["churn_probability"] = [
            float(value)
            for value in churn_probabilities
        ]

        results_df["predicted_ltv"] = [
            float(value)
            for value in predicted_ltv
        ]


        # ----------------------------------------------------
        # 12. Risk level
        # ----------------------------------------------------

        results_df["risk_level"] = [

            "High"
            if probability >= 0.70

            else "Medium"
            if probability >= 0.40

            else "Low"

            for probability in churn_probabilities
        ]


        # ----------------------------------------------------
        # 13. Convert missing values
        # ----------------------------------------------------

        results_df = results_df.fillna("")


        # ----------------------------------------------------
        # 14. Prepare complete CSV for download
        # ----------------------------------------------------

        # Keep the complete prediction results available
        # for the Download Results button.
        latest_prediction_csv = results_df.to_csv(
            index=False
        ).encode("utf-8")


        # ----------------------------------------------------
        # 15. Prepare dashboard results
        # ----------------------------------------------------

        # Return only the first 100 rows to the dashboard.
        # The complete CSV is still available for download.
        display_df = results_df.head(100)

        results = display_df.to_dict(
            orient="records"
        )
        # ----------------------------------------------------
        # 15. Calculate summary values
        # ----------------------------------------------------

        high_risk = sum(
            probability >= 0.70
            for probability in churn_probabilities
        )

        medium_risk = sum(
            0.40 <= probability < 0.70
            for probability in churn_probabilities
        )

        low_risk = sum(
            probability < 0.40
            for probability in churn_probabilities
        )

        churn_count = sum(
            prediction == "Yes"
            for prediction in predicted_churn
        )

        retained_count = sum(
            prediction == "No"
            for prediction in predicted_churn
        )

        # ----------------------------------------------------
        # 16. Build final response
        # ----------------------------------------------------

        response_data = {

            "filename": file.filename,

            "total_customers": int(
                len(results_df)
            ),

            "displayed_customers": int(
                len(results)
            ),

            "predicted_churn": int(
                churn_count
            ),

            "predicted_retained": int(
                retained_count
            ),

            "high_risk_customers": int(
                high_risk
            ),

            "medium_risk_customers": int(
                medium_risk
            ),

            "low_risk_customers": int(
                low_risk
            ),

            "average_churn_probability": float(
                np.mean(churn_probabilities)
            ),

            "average_predicted_ltv": float(
                np.mean(predicted_ltv)
            ),

            "total_predicted_ltv": float(
                np.sum(predicted_ltv)
            ),

            "results": results
        }

        # ----------------------------------------------------
        # 17. Final JSON-safe conversion
        # ----------------------------------------------------

        response_data = make_json_safe(
            response_data
        )

        return JSONResponse(
            content=response_data
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"CSV prediction failed: {str(e)}"
        )
# ============================================================
# DOWNLOAD CSV PREDICTION RESULTS
# ============================================================

@app.get("/dashboard/download-csv")
async def download_csv():

    global latest_prediction_csv

    if latest_prediction_csv is None:
        raise HTTPException(
            status_code=404,
            detail="No CSV prediction results available. Upload and process a CSV first."
        )

    return StreamingResponse(
        io.BytesIO(latest_prediction_csv),
        media_type="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=prediction_results.csv"
        }
    )