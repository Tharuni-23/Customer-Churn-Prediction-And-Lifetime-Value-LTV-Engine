<div align="center">

📊 Customer Churn Prediction & LTV Engine

Predict churn. Estimate customer value. Prioritize retention.

<p>
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-API-green?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-Neon-336791?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/XGBoost-ML-red?logo=xgboost&logoColor=white" alt="XGBoost">
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Metabase-BI-yellow?logo=metabase&logoColor=white" alt="Metabase">
</p>

<p>
  <strong>Production-oriented telecom customer analytics and prediction system</strong>
</p>

</div>

🎯 What This Project Does

This project combines customer analytics, machine learning, automated change detection, scheduled inference, PostgreSQL storage, FastAPI, Docker, and Metabase to support customer-retention decisions.

The system answers two core questions:

Business Question

Prediction

Which customers are likely to churn?

Churn probability + risk level

What is a customer worth?

Predicted Customer Lifetime Value (LTV)

🔄 Business Flow

Customer Data
     ↓
Neon PostgreSQL
     ↓
Change Detection
     ↓
5-Minute Scheduler
     ↓
Preprocessing & Validation
     ↓
┌─────────────────────┬─────────────────────┐
│                     │                     │
▼                     ▼                     │
Churn Model       LTV Model                │
│                     │                     │
└──────────────┬──────┘                     │
               ▼                            │
      Predictions Written Back              │
               ▼                            │
        Neon PostgreSQL                     │
               ▼                            │
           Metabase                         │
               ▼                            │
      Management Decisions                  │

🧠 Core Capabilities

<table>
<tr>
<td width="50%">

🔴 Churn Prediction

XGBoost classification

Churn probability

0.50 classification threshold

High / Medium / Low risk interpretation

</td>
<td width="50%">

💰 LTV Prediction

XGBoost regression

Predicted customer lifetime value

Customer-value segmentation

Risk + value prioritization

</td>
</tr>

<tr>
<td>

⚙️ Automated Processing

Incremental change detection

Five-minute scheduler

Automatic prediction write-back

Processing checkpoint

</td>
<td>

🌐 Application Layer

FastAPI

Single-customer prediction

Dockerized API

Browser-based prediction console

</td>
</tr>
</table>

🛠️ Technology Stack

Layer

Technology

Programming

Python

Data Processing

Pandas, NumPy

Machine Learning

XGBoost, scikit-learn

Database

PostgreSQL

Managed Database

Neon PostgreSQL

Database Access

SQLAlchemy

API

FastAPI + Uvicorn

Frontend

HTML, CSS, JavaScript

BI / Dashboards

Metabase

Containerization

Docker + Docker Compose

Configuration

Environment variables

🏗️ Architecture

                         ┌──────────────────────────────┐
                         │     Customer Console         │
                         │ test_console_single_customer │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │       FastAPI Container      │
                         │           Port 8000          │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │      Neon PostgreSQL         │
                         │       public.customers      │
                         └──────────────┬───────────────┘
                                        │
                              Change Detection
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │     Scheduler Container      │
                         │        Every 5 minutes       │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │      ML Pipeline Container   │
                         │     main.py + preprocessing  │
                         └──────────────┬───────────────┘
                                        │
                            ┌───────────┴───────────┐
                            │                       │
                            ▼                       ▼
                   ┌────────────────┐      ┌────────────────┐
                   │ Churn XGBoost  │      │   LTV XGBoost  │
                   └────────┬───────┘      └────────┬───────┘
                            │                       │
                            └───────────┬───────────┘
                                        ▼
                              Neon PostgreSQL
                                        │
                                        ▼
                                   Metabase

📁 Project Structure

Customer-Churn-Prediction-And-Lifetime-Value-LTV-Engine/
│
├── README.md
├── requirements.txt
├── Dockerfile
├── Dockerfile.frontend
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env.example
│
├── main.py
├── scheduler.py
├── change_tracker.py
├── database.py
├── preprocessing.py
├── final_model.py
├── ltv_model.py
├── test_api_single_customer.py
├── test_data_generator.py
├── dashboard_api.py
│
├── xgboost_model.json
├── ltv_model.json
├── preprocessing_package.pkl
│
├── test_console_single_customer.html
│
├── customer-interface/
│
└── docs/
    └── technical-documentation.md

Runtime files such as .env and pipeline_state.json should not be committed.

🗄️ Neon PostgreSQL

The application uses Neon PostgreSQL as its persistent database.

Environment configuration

Create a local .env file:

DB_USER=your_neon_user
DB_PASSWORD=your_neon_password
DB_HOST=your_neon_host
DB_PORT=5432
DB_NAME=neondb

Main table

public.customers

Important prediction columns:

churn
churn_probability
predicted_ltv
prediction_at

🤖 Machine Learning

Churn Model

The churn model produces:

churn_probability

Classification:

Probability >= 0.50  → Churn = Yes
Probability < 0.50   → Churn = No

Risk interpretation

High Risk     >= 70%
Medium Risk   >= 40%
Low Risk      < 40%

LTV Model

The LTV model produces:

predicted_ltv

This value is used alongside churn probability to prioritize retention actions.

🔁 Incremental Prediction Pipeline

The pipeline is designed to process changed customers, rather than repeatedly processing the full table.

1. Create processing window
2. Fetch changed customers
3. Preprocess customer records
4. Validate feature matrix
5. Generate churn prediction
6. Generate LTV prediction
7. Write predictions back to Neon
8. Update processing checkpoint

Runtime checkpoint:

pipeline_state.json

⏱️ Scheduler

The scheduler runs the processing pipeline on a five-minute interval.

Once Docker is started, the scheduler runs in the background.

You do not manually run the scheduler every five minutes.

Docker starts
     ↓
Scheduler starts
     ↓
Wait / process every 5 minutes
     ↓
Check for changed customers
     ↓
Run ML pipeline
     ↓
Write predictions to Neon
     ↓
Repeat

🌐 FastAPI

The API exposes the prediction service.

Base URL

http://127.0.0.1:8000

Swagger UI

http://127.0.0.1:8000/docs

Main endpoint

POST /predict-single-customer

The endpoint accepts one customer record, applies the project's preprocessing/model pipeline, produces churn and LTV predictions, and writes the prediction result back to Neon PostgreSQL.

🖥️ Customer Prediction Console

The single-customer console is:

test_console_single_customer.html

When served through Docker:

http://127.0.0.1:5500/test_console_single_customer.html

The console displays:

Customer ID

Churn probability

Risk level

Predicted LTV

Database save confirmation

🐳 Docker

The complete application is containerized into four services:

Service

Responsibility

api

FastAPI prediction API

churn-pipeline

ML processing

scheduler

Five-minute automatic execution

frontend

Nginx-served customer console

Prerequisites

docker --version
docker compose version

Build

docker compose build

Start

docker compose up -d

Check containers

docker compose ps

Expected services:

churn-ltv-api
churn-ltv-pipeline
churn-ltv-scheduler
churn-ltv-frontend

View logs

All:

docker compose logs -f

API:

docker compose logs -f api

Pipeline:

docker compose logs -f churn-pipeline

Scheduler:

docker compose logs -f scheduler

Stop

docker compose down

📊 Metabase Management Dashboards

Metabase connects directly to the Neon PostgreSQL database.

The project uses three dashboards with distinct business purposes.

01 — Customer Churn Risk Dashboard

What is happening?

Focuses on:

Overall churn situation

Customer risk distribution

Churn segmentation

Contract / service / payment / tenure analysis

Manager-level filters

02 — Customer LTV & Value Dashboard

What are our customers worth?

Focuses on:

Predicted LTV

Customer-value segments

Revenue exposure

High-value customer analysis

Risk + value relationships

03 — Churn Insights & Retention Strategy

What should management do?

Focuses on:

Churn-risk patterns

Customer behavior signals

Retention opportunities

Management observations

Recommended actions

Things to avoid

Continuous improvement

Business narrative

Dashboard 1
"What is happening?"
        ↓
Dashboard 2
"What is it worth?"
        ↓
Dashboard 3
"What should we do?"

🧪 Controlled Test Data

The project includes a controlled test-data generator.

One test cycle creates:

150 existing-customer updates
+
50 new customer inserts
=
200 affected records

Generated customer IDs use:

TEST-GEN-

This functionality is intended for development/testing and should not be used to create artificial production customer activity.

🔐 Security

Never commit real credentials to GitHub.

Keep these local:

.env
pipeline_state.json

Use:

.env.example

for placeholder configuration.

Example:

DB_USER=your_neon_user
DB_PASSWORD=your_neon_password
DB_HOST=your_neon_host
DB_PORT=5432
DB_NAME=neondb

🌿 Git Branches

Branch

Purpose

main

Stable integrated project

machine-learning

ML experimentation and model development

customer-portal

Customer-facing frontend

integration-pipeline

Integrated database, ML pipeline, scheduler, API and testing

🚀 Quick Start

1. Clone

git clone https://github.com/Tharuni-23/Customer-Churn-Prediction-And-Lifetime-Value-LTV-Engine.git
cd Customer-Churn-Prediction-And-Lifetime-Value-LTV-Engine

2. Configure environment

Create .env using the Neon PostgreSQL credentials.

3. Build containers

docker compose build

4. Start application

docker compose up -d

5. Verify

docker compose ps

6. Open frontend

http://127.0.0.1:5500/test_console_single_customer.html

7. Open API documentation

http://127.0.0.1:8000/docs

8. Open Metabase

Use your configured Metabase instance connected to Neon PostgreSQL.

🔄 End-to-End Demonstration

1. Start Docker
        ↓
2. Open customer console
        ↓
3. Submit / update customer
        ↓
4. Customer data reaches Neon
        ↓
5. Scheduler detects the change
        ↓
6. ML pipeline processes the customer
        ↓
7. Churn probability is generated
        ↓
8. Predicted LTV is generated
        ↓
9. Predictions are written back to Neon
        ↓
10. Metabase reads updated data

📈 Business Outcome

The system is designed to help management:

<table>
<tr>
<td>🎯 Identify customers at risk</td>
<td>💰 Understand customer value</td>
</tr>
<tr>
<td>🔎 Investigate churn patterns</td>
<td>📌 Prioritize retention efforts</td>
</tr>
<tr>
<td>⚙️ Automate prediction processing</td>
<td>📊 Monitor decisions through dashboards</td>
</tr>
</table>

⚠️ Important Analytical Note

Model predictions and segment-level differences are decision-support signals.

A segment with higher churn probability should be investigated further; a relationship in the data should not automatically be interpreted as proof that a particular customer attribute directly causes churn.

👥 Team Project

This repository represents a collaborative implementation covering:

Data processing

Machine learning

Database integration

API development

Automated inference

Dashboarding

Docker deployment

<div align="center">

🚀 Predict → Prioritize → Retain

Customer Churn Prediction & Lifetime Value Engine

</div>