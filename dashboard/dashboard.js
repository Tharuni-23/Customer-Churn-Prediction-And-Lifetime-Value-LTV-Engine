const API_URL = "http://127.0.0.1:8000";


async function fetchJSON(endpoint) {

    const response = await fetch(
        `${API_URL}${endpoint}`
    );

    if (!response.ok) {
        throw new Error(
            `API request failed: ${response.status}`
        );
    }

    return await response.json();
}


// ============================================================
// LOAD SUMMARY
// ============================================================

async function loadSummary() {

    const data =
        await fetchJSON("/dashboard/summary");

    document.getElementById("totalCustomers")
        .textContent =
        data.total_customers;

    document.getElementById("churnedCustomers")
        .textContent =
        data.churned_customers;

    document.getElementById("retainedCustomers")
        .textContent =
        data.retained_customers;

    document.getElementById("avgCharges")
        .textContent =
        `₹${Number(
            data.average_monthly_charges
        ).toFixed(2)}`;

    document.getElementById("monthlyRevenue")
        .textContent =
        `₹${Number(
            data.total_monthly_revenue
        ).toFixed(2)}`;

    document.getElementById("avgLtv")
        .textContent =
        data.average_predicted_ltv !== null
            ? `₹${Number(
                data.average_predicted_ltv
            ).toFixed(2)}`
            : "No predictions";
}


// ============================================================
// LOAD RISK SUMMARY
// ============================================================

async function loadRiskSummary() {

    const data =
        await fetchJSON(
            "/dashboard/risk-summary"
        );

    document.getElementById("highRisk")
        .textContent =
        data.high_risk_customers;

    document.getElementById("mediumRisk")
        .textContent =
        data.medium_risk_customers;

    document.getElementById("lowRisk")
        .textContent =
        data.low_risk_customers;

    document.getElementById("predictionCount")
        .textContent =
        data.customers_with_predictions;
}


// ============================================================
// RISK CLASS
// ============================================================

function getRisk(probability) {

    if (probability === null ||
        probability === undefined) {

        return {
            label: "N/A",
            className: ""
        };
    }


    if (probability >= 0.70) {

        return {
            label: "HIGH",
            className: "risk-high"
        };

    }


    if (probability >= 0.40) {

        return {
            label: "MEDIUM",
            className: "risk-medium"
        };

    }


    return {
        label: "LOW",
        className: "risk-low"
    };
}


// ============================================================
// LOAD TOP RISK CUSTOMERS
// ============================================================

async function loadTopRisk() {

    const data =
        await fetchJSON(
            "/dashboard/top-risk"
        );

    const table =
        document.getElementById(
            "riskTable"
        );

    table.innerHTML = "";


    data.customers.forEach(customer => {

        const risk =
            getRisk(
                customer.churn_probability
            );

        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>
                ${customer.customerID}
            </td>

            <td>
                ${customer.Contract ?? "-"}
            </td>

            <td>
                ${customer.tenure ?? "-"}
            </td>

            <td>
                ₹${Number(
                    customer.MonthlyCharges ?? 0
                ).toFixed(2)}
            </td>

            <td class="${risk.className}">
                ${risk.label}
            </td>

            <td>
                ${(
                    Number(
                        customer.churn_probability
                    ) * 100
                ).toFixed(2)}%
            </td>

            <td>
                ₹${Number(
                    customer.predicted_ltv ?? 0
                ).toFixed(2)}
            </td>

        `;

        table.appendChild(row);

    });
}


// ============================================================
// LOAD ALL CUSTOMERS
// ============================================================

async function loadCustomers() {

    const data =
        await fetchJSON(
            "/dashboard/customers"
        );

    const table =
        document.getElementById(
            "customerTable"
        );

    table.innerHTML = "";


    data.customers.forEach(customer => {

        const probability =
            customer.churn_probability;

        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>
                ${customer.customerID}
            </td>

            <td>
                ${customer.Contract ?? "-"}
            </td>

            <td>
                ${customer.tenure ?? "-"}
            </td>

            <td>
                ₹${Number(
                    customer.MonthlyCharges ?? 0
                ).toFixed(2)}
            </td>

            <td>
                ${customer.Churn ?? "-"}
            </td>

            <td>
                ${customer.predicted_churn ?? "-"}
            </td>

            <td>
                ${
                    probability !== null &&
                    probability !== undefined
                    ? (
                        Number(probability) * 100
                      ).toFixed(2) + "%"
                    : "-"
                }
            </td>

            <td>
                ${
                    customer.predicted_ltv !== null &&
                    customer.predicted_ltv !== undefined
                    ? "₹" +
                      Number(
                          customer.predicted_ltv
                      ).toFixed(2)
                    : "-"
                }
            </td>

        `;

        table.appendChild(row);

    });
}


// ============================================================
// LOAD COMPLETE DASHBOARD
// ============================================================

async function loadDashboard() {

    const error =
        document.getElementById(
            "errorMessage"
        );

    error.textContent = "";


    try {

        await Promise.all([
            loadSummary(),
            loadRiskSummary(),
            loadTopRisk(),
            loadCustomers()
        ]);

    } catch (err) {

        console.error(err);

        error.textContent =
            "Unable to load dashboard data. " +
            "Make sure the FastAPI server is running.";

    }

}


// ============================================================
// INITIAL LOAD
// ============================================================

loadDashboard();