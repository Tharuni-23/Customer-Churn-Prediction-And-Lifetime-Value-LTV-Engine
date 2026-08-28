
## Machine Learning Models

Three models were evaluated for customer churn prediction: Logistic Regression, Artificial Neural Network (ANN), and XGBoost.


## Model Comparison

ANN achieved the highest accuracy at 75.16%. Logistic Regression achieved 73.95% accuracy. Tuned XGBoost achieved 74.24% accuracy, with the highest recall of 80.75% and highest ROC-AUC of 0.8463.


## Model Selection

XGBoost was selected because it achieved the highest recall and ROC-AUC among the evaluated models. Higher recall is important for churn prediction because it helps identify more customers who are actually likely to leave. ANN remains a potential future improvement because it is more data-hungry.


## Project Overview
This project predicts customer churn and estimates customer lifetime value using machine learning.

## Dataset
The project uses the IBM Telco Customer Churn dataset for customer churn analysis.

## Data Preprocessing
The data was cleaned, encoded, and prepared before training the machine learning models.

## Logistic Regression
Logistic Regression was used as a baseline classification model for churn prediction.

## Artificial Neural Network
ANN was evaluated as a nonlinear model and achieved 75.16% accuracy.

## XGBoost
Tuned XGBoost achieved 74.24% accuracy, 80.75% recall, and 0.8463 ROC-AUC.
