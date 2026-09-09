<div align="center">

# Customer Churn Prediction & Lifetime Value (LTV) Engine

### An integrated machine learning system for customer churn prediction and Lifetime Value estimation

<p>
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/XGBoost-Machine%20Learning-orange" alt="XGBoost">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Neon-PostgreSQL-black" alt="Neon">
  <img src="https://img.shields.io/badge/HTML%2FCSS%2FJS-Frontend-E34F26" alt="Frontend">
</p>

</div>

---

## Overview

Customer Churn Prediction & Lifetime Value (LTV) Engine is a team-developed project for analyzing customer behavior and generating two important business predictions:

**Customer Churn Probability** and **Customer Lifetime Value (LTV)**.

The system combines machine learning, customer data processing, Neon PostgreSQL, scheduled prediction, FastAPI services, controlled test-data generation, and a customer-facing web interface.

The repository is divided into separate branches so that machine learning development, customer portal development, and the integrated prediction system can be developed independently.

---

## Objectives

<table>
<tr>
<td>

### Prediction

Predict the probability that a customer will churn.

</td>
<td>

### Customer Value

Estimate the expected Lifetime Value of a customer.

</td>
</tr>

<tr>
<td>

### Change Detection

Detect newly inserted and updated customer records.

</td>
<td>

### Automation

Automatically process changed records through the prediction pipeline.

</td>
</tr>

<tr>
<td>

### Database Integration

Store customer information and prediction results in PostgreSQL.

</td>
<td>

### Customer Experience

Provide a customer-facing portal for account and subscription management.

</td>
</tr>
</table>

---

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python |
| Machine Learning | Scikit-learn, XGBoost |
| Data Processing | Pandas, NumPy |
| Database | PostgreSQL, Neon PostgreSQL |
| Database Access | SQLAlchemy |
| Backend API | FastAPI |
| Frontend | HTML5, CSS3, JavaScript |
| Scheduling | Python Scheduler |
| Model Storage | JSON, PKL |

---

## System Architecture

<div align="center">

```text
                         CUSTOMER / TEST INTERFACE
                                    |
                                    v
                                 FastAPI
                                    |
                                    v
                           Neon PostgreSQL
                                    |
                                    v
                           Change Detection
                                    |
                                    v
                               Scheduler
                                    |
                                    v
                            Preprocessing
                                    |
                         +----------+----------+
                         |                     |
                         v                     v
                  Churn Prediction       LTV Prediction
                         |                     |
                         +----------+----------+
                                    |
                                    v
                           Prediction Results
                                    |
                                    v
                           Neon PostgreSQL