const API_URL = "http://127.0.0.1:8000";

let riskChart = null;


// ============================================================
// GENERIC API REQUEST
// ============================================================

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

    // Render chart using the same API data
    renderRiskChart(data);
}


// ============================================================
// RISK CLASS
// ============================================================

function getRisk(probability) {

    if (
        probability === null ||
        probability === undefined
    ) {
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

        const probability =
            customer.churn_probability;

        const probabilityText =
            probability !== null &&
            probability !== undefined
                ? `${(
                    Number(probability) * 100
                ).toFixed(2)}%`
                : "-";

        const ltvText =
            customer.predicted_ltv !== null &&
            customer.predicted_ltv !== undefined
                ? `₹${Number(
                    customer.predicted_ltv
                ).toFixed(2)}`
                : "-";

        const chargesText =
            customer.MonthlyCharges !== null &&
            customer.MonthlyCharges !== undefined
                ? `₹${Number(
                    customer.MonthlyCharges
                ).toFixed(2)}`
                : "-";

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
                ${chargesText}
            </td>

            <td class="${risk.className}">
                ${risk.label}
            </td>

            <td>
                ${probabilityText}
            </td>

            <td>
                ${ltvText}
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

        const probabilityText =
            probability !== null &&
            probability !== undefined
                ? `${(
                    Number(probability) * 100
                ).toFixed(2)}%`
                : "-";

        const ltvText =
            customer.predicted_ltv !== null &&
            customer.predicted_ltv !== undefined
                ? `₹${Number(
                    customer.predicted_ltv
                ).toFixed(2)}`
                : "-";

        const chargesText =
            customer.MonthlyCharges !== null &&
            customer.MonthlyCharges !== undefined
                ? `₹${Number(
                    customer.MonthlyCharges
                ).toFixed(2)}`
                : "-";

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
                ${chargesText}
            </td>

            <td>
                ${customer.Churn ?? "-"}
            </td>

            <td>
                ${customer.predicted_churn ?? "-"}
            </td>

            <td>
                ${probabilityText}
            </td>

            <td>
                ${ltvText}
            </td>

        `;

        table.appendChild(row);

    });
}


// ============================================================
// RENDER RISK CHART
// ============================================================

function renderRiskChart(riskData) {

    const canvas =
        document.getElementById("riskChart");

    if (!canvas) {

        console.error(
            "riskChart canvas not found"
        );

        return;
    }

    if (typeof Chart === "undefined") {

        console.error(
            "Chart.js is not loaded"
        );

        return;
    }


    // Destroy previous chart when Refresh is clicked
    if (riskChart !== null) {

        riskChart.destroy();

        riskChart = null;
    }


    riskChart = new Chart(
        canvas,
        {
            type: "bar",

            data: {

                labels: [
                    "High Risk",
                    "Medium Risk",
                    "Low Risk"
                ],

                datasets: [
                    {
                        label: "Customers",

                        data: [
                            Number(
                                riskData.high_risk_customers
                            ),

                            Number(
                                riskData.medium_risk_customers
                            ),

                            Number(
                                riskData.low_risk_customers
                            )
                        ]
                    }
                ]
            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    y: {

                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        }

                    }

                },

                plugins: {

                    legend: {
                        display: true
                    }

                }

            }
        }
    );
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
// SEARCH CUSTOMER
// ============================================================

async function searchCustomer() {

    const customerId =
        document.getElementById(
            "customerSearch"
        ).value.trim();

    const details =
        document.getElementById(
            "customerDetails"
        );


    if (!customerId) {

        details.innerHTML =
            "<p>Please enter a Customer ID.</p>";

        return;
    }


    try {

        const customer =
            await fetchJSON(
                `/dashboard/customers/${customerId}`
            );


        const risk =
            getRisk(
                customer.churn_probability
            );


        const probabilityText =
            customer.churn_probability !== null &&
            customer.churn_probability !== undefined
                ? `${(
                    Number(
                        customer.churn_probability
                    ) * 100
                ).toFixed(2)}%`
                : "-";


        const ltvText =
            customer.predicted_ltv !== null &&
            customer.predicted_ltv !== undefined
                ? `₹${Number(
                    customer.predicted_ltv
                ).toFixed(2)}`
                : "-";


        const chargesText =
            customer.MonthlyCharges !== null &&
            customer.MonthlyCharges !== undefined
                ? `₹${Number(
                    customer.MonthlyCharges
                ).toFixed(2)}`
                : "-";


        details.innerHTML = `

            <div class="customer-detail-grid">

                <div>
                    <strong>Customer ID</strong>
                    <span>
                        ${customer.customerID}
                    </span>
                </div>


                <div>
                    <strong>Contract</strong>
                    <span>
                        ${customer.Contract ?? "-"}
                    </span>
                </div>


                <div>
                    <strong>Tenure</strong>
                    <span>
                        ${customer.tenure ?? "-"} months
                    </span>
                </div>


                <div>
                    <strong>Monthly Charges</strong>
                    <span>
                        ${chargesText}
                    </span>
                </div>


                <div>
                    <strong>Actual Churn</strong>
                    <span>
                        ${customer.Churn ?? "-"}
                    </span>
                </div>


                <div>
                    <strong>Predicted Churn</strong>
                    <span>
                        ${customer.predicted_churn ?? "-"}
                    </span>
                </div>


                <div>
                    <strong>Churn Probability</strong>
                    <span class="${risk.className}">
                        ${probabilityText}
                    </span>
                </div>


                <div>
                    <strong>Risk Level</strong>
                    <span class="${risk.className}">
                        ${risk.label}
                    </span>
                </div>


                <div>
                    <strong>Predicted LTV</strong>
                    <span>
                        ${ltvText}
                    </span>
                </div>

            </div>

        `;

    } catch (err) {

        console.error(err);

        details.innerHTML =
            "<p class='error'>" +
            "Customer not found or API error." +
            "</p>";

    }
}


// ============================================================
// SEARCH USING ENTER KEY
// ============================================================

document
    .getElementById("customerSearch")
    .addEventListener(
        "keydown",
        function(event) {

            if (event.key === "Enter") {

                searchCustomer();

            }

        }
    );


// ============================================================
// INITIAL LOAD
// ============================================================

loadDashboard();
// ============================================================
// CSV UPLOAD AND PREDICTION
// ============================================================

async function uploadCSV() {

    const fileInput = document.getElementById("csvFile");
    const uploadButton = document.getElementById("uploadCsvBtn");
    const status = document.getElementById("uploadStatus");

    if (!fileInput.files.length) {

        status.textContent = "Please select a CSV file first.";
        return;
    }

    const file = fileInput.files[0];

    if (!file.name.toLowerCase().endsWith(".csv")) {

        status.textContent = "Please select a valid CSV file.";
        return;
    }

    const formData = new FormData();

    formData.append("file", file);

    uploadButton.disabled = true;
    uploadButton.textContent = "Processing...";

    status.textContent =
        "Uploading CSV and generating predictions...";

    try {

        const response = await fetch(
            `${API_URL}/dashboard/upload-csv`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail || "CSV processing failed"
            );
        }

        // ----------------------------------------------------
        // Display summary
        // ----------------------------------------------------

        document.getElementById(
            "csvSummarySection"
        ).style.display = "block";

        document.getElementById(
            "csvTotalCustomers"
        ).textContent = data.total_customers;

        document.getElementById(
            "csvChurned"
        ).textContent = data.predicted_churn;

        document.getElementById(
            "csvRetained"
        ).textContent = data.predicted_retained;

        document.getElementById(
            "csvHighRisk"
        ).textContent = data.high_risk_customers;

        document.getElementById(
            "csvMediumRisk"
        ).textContent = data.medium_risk_customers;

        document.getElementById(
            "csvLowRisk"
        ).textContent = data.low_risk_customers;

        document.getElementById(
            "csvAvgLtv"
        ).textContent =
            `₹${Number(
                data.average_predicted_ltv
            ).toFixed(2)}`;


        // ----------------------------------------------------
        // Display prediction table
        // ----------------------------------------------------

        const tbody = document.getElementById(
            "csvResultsBody"
        );

        tbody.innerHTML = "";

        data.results.forEach(customer => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>
                    ${customer.customerID ?? "-"}
                </td>

                <td>
                    ${customer.Contract ?? "-"}
                </td>

                <td>
                    ${customer.tenure ?? "-"}
                </td>

                <td>
                    ₹${Number(
                        customer.MonthlyCharges || 0
                    ).toFixed(2)}
                </td>

                <td>
                    ${customer.predicted_churn ?? "-"}
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
                        customer.predicted_ltv || 0
                    ).toFixed(2)}
                </td>

                <td>
                    ${customer.risk_level ?? "-"}
                </td>
            `;

            tbody.appendChild(row);
        });


        // ----------------------------------------------------
        // Display information
        // ----------------------------------------------------

        document.getElementById(
            "csvDisplayedInfo"
        ).textContent =
            `Showing ${data.displayed_customers ?? data.results.length} ` +
            `of ${data.total_customers} customers from ` +
            `${data.filename}.`;


        status.textContent =
            "CSV processed successfully.";

    }

    catch (error) {

        console.error(
            "CSV upload error:",
            error
        );

        status.textContent =
            `Error: ${error.message}`;

        document.getElementById(
            "csvSummarySection"
        ).style.display = "none";

    }

    finally {

        uploadButton.disabled = false;
        uploadButton.textContent = "Process CSV";
    }
}
// ============================================================
// DOWNLOAD CSV PREDICTION RESULTS
// ============================================================

function downloadCSV() {

    window.location.href =
        `${API_URL}/dashboard/download-csv`;
}