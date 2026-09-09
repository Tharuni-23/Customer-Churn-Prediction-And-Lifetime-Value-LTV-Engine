# Customer Churn Prediction and Lifetime Value (LTV) Engine

Team project developed during the Zaalima Development Pvt. Ltd. internship.

The project combines Machine Learning, PostgreSQL, FastAPI, and a Manager Dashboard to analyze customer churn risk and estimate Customer Lifetime Value (LTV).

---

## Project Overview

The system is designed to help managers identify customers who are likely to churn and understand their expected lifetime value.

The main workflow is:

Customer Data
    ↓
Data Preprocessing
    ↓
Feature Engineering
    ↓
Machine Learning Models
    ↓
Churn Probability + Predicted LTV
    ↓
PostgreSQL Database
    ↓
FastAPI Backend
    ↓
Manager Dashboard

The system supports both existing database customers and CSV-based batch prediction.

---

## Key Features

### 1. Customer Churn Prediction

The system predicts whether a customer is likely to churn.

The churn model produces:

- Predicted churn (`Yes` / `No`)
- Churn probability

A probability threshold of 0.50 is used for the churn prediction.

---

### 2. Customer Lifetime Value (LTV) Prediction

The system predicts the expected Customer Lifetime Value for each customer.

The dashboard provides:

- Individual predicted LTV
- Average predicted LTV
- Total predicted LTV for uploaded CSV data

---

### 3. Churn Risk Classification

Customers are classified into three risk levels using their churn probability:

| Probability | Risk Level |
|-------------|------------|
| 70% and above | High |
| 40% to below 70% | Medium |
| Below 40% | Low |

This allows managers to quickly identify customers who require attention.

---

### 4. Manager Dashboard

The Manager Dashboard provides an overview of customer and prediction information.

The dashboard displays:

- Total customers
- Churned customers
- Retained customers
- Average monthly charges
- Monthly revenue
- Average predicted LTV
- High-risk customers
- Medium-risk customers
- Low-risk customers
- Number of customers with predictions
- Risk distribution chart
- Top at-risk customers
- Customer search
- Customer prediction details

---

### 5. Top At-Risk Customers

The dashboard displays the customers with the highest churn probabilities.

The table includes:

- Customer ID
- Contract
- Tenure
- Monthly Charges
- Risk Level
- Churn Probability
- Predicted LTV

This helps managers prioritize customer retention activities.

---

### 6. Customer Search

Managers can search for an individual customer using the Customer ID.

The customer details include the available customer information along with:

- Predicted churn
- Churn probability
- Predicted LTV
- Prediction timestamp

---

### 7. CSV Upload and Batch Prediction

The Manager Dashboard supports CSV file upload.

The uploaded CSV is:

1. Read by the FastAPI backend
2. Preprocessed using the saved preprocessing package
3. Passed through the churn model
4. Passed through the LTV model
5. Assigned a risk level
6. Returned as prediction results

The dashboard displays the prediction results for the uploaded customers.

For large files, the dashboard displays the first 100 rows while the complete file is processed.

---

### 8. Download Prediction Results

After processing an uploaded CSV, the manager can download the complete prediction results.

The downloaded file contains prediction information such as:

- Customer ID
- Contract
- Tenure
- Monthly Charges
- Predicted Churn
- Churn Probability
- Predicted LTV
- Risk Level

The downloaded file is generated as:

`prediction_results.csv`

---

## Machine Learning

The project uses trained Machine Learning models for:

### Churn Prediction

An XGBoost classification model is used to predict customer churn probability.

Model artifact:

`xgboost_model.json`

### LTV Prediction

An XGBoost regression model is used to estimate Customer Lifetime Value.

Model artifact:

`ltv_model.json`

### Preprocessing

The saved preprocessing package is used to transform customer data into the same feature representation expected by the trained models.

Artifact:

`preprocessing_package.pkl`

---

## Feature Engineering

The project includes engineered customer features such as:

- Tenure Group
- Total Services
- Mails

These features are used along with the original customer attributes during prediction.

The final preprocessing pipeline produces the feature representation required by the trained ML models.

---

## Database

The Manager Dashboard uses PostgreSQL for customer data and prediction storage.

The main local customer table is:

`customer_churn`

Prediction fields include:

- `predicted_churn`
- `churn_probability`
- `predicted_ltv`
- `prediction_at`

The original customer churn value is preserved separately from the model prediction.

This prevents the historical target value from being overwritten by the prediction.

---

## Backend

The backend is implemented using FastAPI.

The API provides customer data, dashboard analytics, predictions, risk analysis, and CSV processing.

### Main API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Check whether the API is running |
| GET | `/health` | Check API/database health |
| GET | `/dashboard/summary` | Get dashboard summary statistics |
| GET | `/customers` | Get customer records |
| GET | `/customers/{customer_id}` | Get an individual customer |
| GET | `/dashboard/customers` | Get dashboard customer data |
| GET | `/dashboard/customers/{customer_id}` | Get dashboard customer details |
| GET | `/dashboard/risk-summary` | Get high/medium/low risk counts |
| GET | `/dashboard/top-risk` | Get top at-risk customers |
| POST | `/predict/{customer_id}` | Generate prediction for one customer |
| POST | `/dashboard/upload-csv` | Upload CSV and generate predictions |
| GET | `/dashboard/download-csv` | Download latest CSV prediction results |

---

## Dashboard Summary

The dashboard summary provides:

- Total customer count
- Churned customer count
- Retained customer count
- Average monthly charges
- Total monthly revenue
- Average predicted LTV

Example values from the local Telco customer dataset include:

- Total customers: 7043
- Churned customers: 1869
- Retained customers: 5174

---

## Technologies Used

### Programming

- Python
- HTML
- CSS
- JavaScript

### Backend

- FastAPI
- Uvicorn

### Database

- PostgreSQL
- SQLAlchemy
- psycopg2

### Machine Learning

- XGBoost
- pandas
- NumPy
- scikit-learn
- joblib

### Visualization

- Chart.js

### Version Control

- Git
- GitHub

---

## Project Structure

```text
Customer-Churn-Prediction-And-Lifetime-Value-LTV-Engine/
│
├── dashboard/
│   ├── dashboard.js
│   ├── index.html
│   └── style.css
│
├── src/
│   ├── api.py
│   ├── database.py
│   └── prediction_pipeline.py
│
├── sql/
│   └── add_prediction_columns.sql
│
├── preprocessing.py
├── preprocessing_package.pkl
├── xgboost_model.json
├── ltv_model.json
│
├── README.md
├── .gitignore
└── .env