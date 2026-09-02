# Customer-Churn-Prediction-And-Lifetime-Value-LTV-Engine
Team project developed during the Zaalima internship. 

## Manager Dashboard API

The Manager Dashboard uses FastAPI to retrieve customer information
from the PostgreSQL database.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Check whether the API is running |
| GET | `/health` | Check API and PostgreSQL database connectivity |
| GET | `/dashboard/summary` | Get overall customer and revenue statistics |
| GET | `/customers` | Get a list of customers |
| GET | `/customers/{customer_id}` | Get details of a specific customer |

### Dashboard Summary

The `/dashboard/summary` endpoint provides:

- Total number of customers
- Number of churned customers
- Number of retained customers
- Average monthly charges
- Total monthly revenue

### Technology

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy