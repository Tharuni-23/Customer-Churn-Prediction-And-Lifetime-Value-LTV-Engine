<div align="center">

<h1>Machine Learning — Customer Churn & Lifetime Value</h1>

<p>
  <strong>Model Development • Experimentation • Preprocessing • Comparison</strong>
</p>

<br>

<img src="https://img.shields.io/badge/Python-3.x-blue?logo=python">
<img src="https://img.shields.io/badge/ANN-Experimentation-purple">
<img src="https://img.shields.io/badge/Logistic%20Regression-Classification-orange">
<img src="https://img.shields.io/badge/XGBoost-Model-green">
<img src="https://img.shields.io/badge/Machine%20Learning-Research-brightgreen">

</div>

---

<h2>Overview</h2>

<p>
This branch contains the machine learning development work for the
<strong>Customer Churn Prediction & Lifetime Value (LTV) Engine</strong>.
</p>

<p>
The main purpose of this branch is to experiment with different machine
learning approaches, prepare customer data, evaluate model behavior,
and compare candidate algorithms before integrating the selected models
into the complete prediction system.
</p>

---

<h2>Objectives</h2>

<table>
<tr>
<td width="50%">

<h3>Customer Churn</h3>

<p>
Develop models that estimate the likelihood of a customer leaving the service.
</p>

</td>

<td width="50%">

<h3>Lifetime Value</h3>

<p>
Develop a model for estimating the expected Lifetime Value of a customer.
</p>

</td>
</tr>

<tr>
<td>

<h3>Model Experimentation</h3>

<p>
Explore different machine learning approaches and compare their behavior.
</p>

</td>

<td>

<h3>Data Preparation</h3>

<p>
Prepare and transform customer data into a format suitable for model training.
</p>

</td>
</tr>
</table>

---

<h2>Machine Learning Approaches</h2>

<table>
<tr>
<th>Approach</th>
<th>Purpose</th>
<th>Related Work</th>
</tr>

<tr>
<td><strong>Artificial Neural Network (ANN)</strong></td>
<td>Churn prediction experimentation</td>
<td>
<code>ANNfeeding.ipynb</code><br>
<code>Ann_test.ipynb</code>
</td>
</tr>

<tr>
<td><strong>Logistic Regression</strong></td>
<td>Traditional churn classification</td>
<td>
<code>logistic.ipynb</code><br>
<code>logistic_largedataset.ipynb</code>
</td>
</tr>

<tr>
<td><strong>XGBoost</strong></td>
<td>Tree-based churn prediction</td>
<td>
<code>xgboost.ipynb</code>
</td>
</tr>

</table>

---

<h2>Model Comparison</h2>

<p>
The different churn prediction approaches are evaluated and compared
using:
</p>

<p align="center">

<strong>
<code>Churn_Model_Comparison.ipynb</code>
</strong>

</p>

<p>
The comparison focuses on understanding how the candidate models behave
on the customer churn dataset and identifying a suitable approach for
the integrated prediction pipeline.
</p>

```text
                 Customer Dataset
                        |
                        v
                 Feature Preparation
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
         ANN       Logistic       XGBoost
          |             |             |
          +-------------+-------------+
                        |
                        v
                 Model Comparison
                        |
                        v
                  Model Evaluation