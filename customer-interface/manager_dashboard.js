// =========================================================
// CONFIGURATION
// =========================================================

const API_BASE_URL = "http://127.0.0.1:8000";


// =========================================================
// CHART INSTANCES
// =========================================================

const charts = {};


// =========================================================
// FORMATTING HELPERS
// =========================================================

function numberFormat(value) {
    return Number(value || 0).toLocaleString("en-IN");
}


function currencyFormat(value) {
    return "₹" + Number(value || 0).toLocaleString(
        "en-IN",
        {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    );
}


function percentFormat(value) {
    return (Number(value || 0) * 100).toFixed(2) + "%";
}


function valueOrNA(value) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "N/A";
    }

    return String(value);
}


function dateFormat(value) {

    if (!value) {
        return "N/A";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return date.toLocaleString("en-IN");
}


// =========================================================
// API HELPER
// =========================================================

async function getJSON(endpoint) {

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`
    );

    if (!response.ok) {

        let message =
            `Request failed: ${response.status}`;

        try {

            const errorData = await response.json();

            if (errorData.detail) {
                message = errorData.detail;
            }

        } catch (_) {
            // Response may not contain JSON.
        }

        throw new Error(message);
    }

    return await response.json();
}


// =========================================================
// API HEALTH
// =========================================================

async function checkAPI() {

    const statusText =
        document.getElementById("apiStatus");

    const statusDot =
        document.getElementById("statusDot");

    try {

        await getJSON("/");

        statusText.textContent =
            "API Connected";

        statusDot.className =
            "status-dot online";

    } catch (error) {

        console.error(
            "API health check failed:",
            error
        );

        statusText.textContent =
            "API Disconnected";

        statusDot.className =
            "status-dot offline";
    }
}


// =========================================================
// SUMMARY / KPI CARDS
// =========================================================

async function loadSummary() {

    const data =
        await getJSON(
            "/dashboard/summary"
        );


    document.getElementById(
        "totalCustomers"
    ).textContent =
        numberFormat(
            data.total_customers
        );


    document.getElementById(
        "churnCustomers"
    ).textContent =
        numberFormat(
            data.churn_customers
        );


    document.getElementById(
        "churnRate"
    ).textContent =
        percentFormat(
            data.churn_rate
        );


    document.getElementById(
        "highRiskCustomers"
    ).textContent =
        numberFormat(
            data.high_risk_customers
        );


    document.getElementById(
        "avgPredictedLtv"
    ).textContent =
        currencyFormat(
            data.avg_predicted_ltv
        );


    document.getElementById(
        "totalPredictedLtv"
    ).textContent =
        currencyFormat(
            data.total_predicted_ltv
        );


    document.getElementById(
        "priorityCustomersCount"
    ).textContent =
        numberFormat(
            data.high_risk_high_ltv_customers
        );


    document.getElementById(
        "avgMonthlyCharges"
    ).textContent =
        currencyFormat(
            data.avg_monthly_charges
        );


    document.getElementById(
        "lastUpdated"
    ).textContent =
        `Updated: ${new Date().toLocaleString("en-IN")}`;
}


// =========================================================
// CHART DESTROY HELPER
// =========================================================

function destroyChart(name) {

    if (charts[name]) {

        charts[name].destroy();

        charts[name] = null;
    }
}


// =========================================================
// CHURN VS RETAINED
// =========================================================

async function loadChurnOutcomeChart() {

    const data =
        await getJSON(
            "/dashboard/summary"
        );


    destroyChart("churnOutcome");


    charts.churnOutcome =
        new Chart(
            document.getElementById(
                "churnOutcomeChart"
            ),
            {

                type: "doughnut",

                data: {

                    labels: [
                        "Retained",
                        "Churn"
                    ],

                    datasets: [

                        {
                            data: [
                                data.retained_customers,
                                data.churn_customers
                            ],

                            borderWidth: 2
                        }
                    ]
                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            position: "bottom"
                        },

                        tooltip: {

                            callbacks: {

                                label: function(context) {

                                    return (
                                        `${context.label}: ` +
                                        numberFormat(
                                            context.raw
                                        )
                                    );
                                }
                            }
                        }
                    }
                }
            }
        );
}


// =========================================================
// GLOBAL CHURN RISK
// =========================================================

async function loadChurnRiskChart() {

    const result =
        await getJSON(
            "/dashboard/churn-risk"
        );


    const labels =
        result.risk_distribution.map(
            item => item.risk_level
        );


    const values =
        result.risk_distribution.map(
            item => Number(
                item.customer_count || 0
            )
        );


    destroyChart("churnRisk");


    charts.churnRisk =
        new Chart(
            document.getElementById(
                "churnRiskChart"
            ),
            {

                type: "doughnut",

                data: {

                    labels: labels,

                    datasets: [

                        {
                            data: values,

                            borderWidth: 2
                        }
                    ]
                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            position: "bottom"
                        },

                        tooltip: {

                            callbacks: {

                                label: function(context) {

                                    return (
                                        `${context.label}: ` +
                                        numberFormat(
                                            context.raw
                                        )
                                    );
                                }
                            }
                        }
                    }
                }
            }
        );
}


// =========================================================
// LTV SEGMENTATION
// =========================================================

async function loadLtvChart() {

    const result =
        await getJSON(
            "/dashboard/ltv-segments"
        );


    const labels =
        result.ltv_segments.map(
            item => item.ltv_segment
        );


    const values =
        result.ltv_segments.map(
            item => Number(
                item.customer_count || 0
            )
        );


    destroyChart("ltv");


    charts.ltv =
        new Chart(
            document.getElementById(
                "ltvSegmentChart"
            ),
            {

                type: "bar",

                data: {

                    labels: labels,

                    datasets: [

                        {
                            label:
                                "Customers",

                            data: values,

                            borderWidth: 1
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

                            display: false
                        },

                        tooltip: {

                            callbacks: {

                                label: function(context) {

                                    return (
                                        ` Customers: ` +
                                        numberFormat(
                                            context.raw
                                        )
                                    );
                                }
                            }
                        }
                    }
                }
            }
        );
}


// =========================================================
// GENERIC CATEGORY CHART
// =========================================================

async function loadCategoryChart(
    endpoint,
    canvasId,
    chartName,
    fieldName
) {

    const result =
        await getJSON(endpoint);


    const labels =
        result.data.map(
            item =>
                valueOrNA(
                    item[fieldName]
                )
        );


    const values =
        result.data.map(
            item =>
                Number(
                    item.churn_customers || 0
                )
        );


    destroyChart(chartName);


    charts[chartName] =
        new Chart(
            document.getElementById(
                canvasId
            ),
            {

                type: "bar",

                data: {

                    labels: labels,

                    datasets: [

                        {
                            label:
                                "Churn Customers",

                            data: values,

                            borderWidth: 1
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

                            display: false
                        },

                        tooltip: {

                            callbacks: {

                                label: function(context) {

                                    return (
                                        ` Churn: ` +
                                        numberFormat(
                                            context.raw
                                        )
                                    );
                                }
                            }
                        }
                    }
                }
            }
        );
}


// =========================================================
// CATEGORY CHARTS
// =========================================================

async function loadGenderChart() {

    await loadCategoryChart(
        "/dashboard/churn-by-gender",
        "genderChart",
        "gender",
        "gender"
    );
}


async function loadPartnerChart() {

    await loadCategoryChart(
        "/dashboard/churn-by-partner",
        "partnerChart",
        "partner",
        "partner"
    );
}


async function loadContractChart() {

    await loadCategoryChart(
        "/dashboard/churn-by-contract",
        "contractChart",
        "contract",
        "contract"
    );
}


async function loadInternetChart() {

    await loadCategoryChart(
        "/dashboard/churn-by-internet",
        "internetChart",
        "internet",
        "internet_service"
    );
}


async function loadTenureChart() {

    await loadCategoryChart(
        "/dashboard/churn-by-tenure",
        "tenureChart",
        "tenure",
        "tenure_segment"
    );
}


async function loadPaymentChart() {

    await loadCategoryChart(
        "/dashboard/churn-by-payment",
        "paymentChart",
        "payment",
        "payment_method"
    );
}


async function loadServicesChart() {

    await loadCategoryChart(
        "/dashboard/churn-by-services",
        "servicesChart",
        "services",
        "total_services"
    );
}


// =========================================================
// CUSTOMER TABLE
// =========================================================

async function loadCustomers() {

    const result =
        await getJSON(
            "/dashboard/customers"
        );


    const tbody =
        document.getElementById(
            "customerTableBody"
        );


    tbody.innerHTML = "";


    if (
        !result.customers ||
        result.customers.length === 0
    ) {

        tbody.innerHTML = `

            <tr>

                <td
                    colspan="5"
                    class="loading"
                >
                    No predicted customers found.
                </td>

            </tr>

        `;

        return;
    }


    result.customers.forEach(
        customer => {

            const row =
                document.createElement(
                    "tr"
                );


            row.classList.add(
                "clickable"
            );


            const churn =
                customer.churn ??
                "N/A";


            const churnClass =
                churn === "Yes"
                    ? "churn-yes"
                    : churn === "No"
                        ? "churn-no"
                        : "";


            addCell(
                row,
                customer.customerid
            );


            addCell(
                row,
                churn,
                churnClass
            );


            addCell(
                row,
                customer.churn_probability != null
                    ? percentFormat(
                        customer.churn_probability
                    )
                    : "N/A"
            );


            addCell(
                row,
                customer.predicted_ltv != null
                    ? currencyFormat(
                        customer.predicted_ltv
                    )
                    : "N/A"
            );


            addCell(
                row,
                dateFormat(
                    customer.prediction_at
                )
            );


            row.addEventListener(
                "click",
                () => {

                    if (!customer.customerid) {
                        return;
                    }


                    document.getElementById(
                        "customerIdInput"
                    ).value =
                        customer.customerid;


                    searchCustomer(
                        customer.customerid
                    );
                }
            );


            tbody.appendChild(
                row
            );
        }
    );
}


// =========================================================
// PRIORITY CUSTOMERS
// =========================================================

async function loadPriorityCustomers() {

    const result =
        await getJSON(
            "/dashboard/priority-customers"
        );


    const tbody =
        document.getElementById(
            "priorityTableBody"
        );


    tbody.innerHTML = "";


    if (
        !result.priority_customers ||
        result.priority_customers.length === 0
    ) {

        tbody.innerHTML = `

            <tr>

                <td
                    colspan="7"
                    class="loading"
                >
                    No high-risk, high-LTV customers found.
                </td>

            </tr>

        `;

        return;
    }


    result.priority_customers.forEach(
        customer => {

            const row =
                document.createElement(
                    "tr"
                );


            row.classList.add(
                "clickable"
            );


            addCell(
                row,
                customer.customerid
            );


            addCell(
                row,
                percentFormat(
                    customer.churn_probability
                ),
                "churn-yes"
            );


            addCell(
                row,
                currencyFormat(
                    customer.predicted_ltv
                )
            );


            addCell(
                row,
                valueOrNA(
                    customer.contract
                )
            );


            addCell(
                row,
                customer.tenure != null
                    ? `${customer.tenure} months`
                    : "N/A"
            );


            addCell(
                row,
                customer.monthlycharges != null
                    ? currencyFormat(
                        customer.monthlycharges
                    )
                    : "N/A"
            );


            addCell(
                row,
                dateFormat(
                    customer.prediction_at
                )
            );


            row.addEventListener(
                "click",
                () => {

                    if (!customer.customerid) {
                        return;
                    }


                    document.getElementById(
                        "customerIdInput"
                    ).value =
                        customer.customerid;


                    searchCustomer(
                        customer.customerid
                    );
                }
            );


            tbody.appendChild(
                row
            );
        }
    );
}


// =========================================================
// TABLE CELL CREATION
// =========================================================

function addCell(
    row,
    value,
    className = ""
) {

    const cell =
        document.createElement(
            "td"
        );


    cell.textContent =
        valueOrNA(value);


    if (className) {
        cell.className =
            className;
    }


    row.appendChild(
        cell
    );
}


// =========================================================
// CUSTOMER SEARCH
// =========================================================

async function searchCustomer(
    customerId
) {

    const messageElement =
        document.getElementById(
            "searchMessage"
        );


    const detailsSection =
        document.getElementById(
            "customerDetailsSection"
        );


    messageElement.textContent =
        "";


    if (
        !customerId ||
        customerId.trim() === ""
    ) {

        detailsSection.classList.add(
            "hidden"
        );


        messageElement.textContent =
            "Please enter a Customer ID.";

        return;
    }


    customerId =
        customerId.trim();


    try {

        const result =
            await getJSON(
                `/dashboard/customer/${encodeURIComponent(customerId)}`
            );


        displayCustomer(
            result.customer
        );


    } catch (error) {

        console.error(
            "Customer search failed:",
            error
        );


        detailsSection.classList.add(
            "hidden"
        );


        messageElement.textContent =
            error.message;
    }
}


// =========================================================
// DISPLAY CUSTOMER DETAILS
// IMPORTANT:
// These field names exactly match the API response.
// =========================================================

function displayCustomer(
    customer
) {

    const detailsSection =
        document.getElementById(
            "customerDetailsSection"
        );


    detailsSection.classList.remove(
        "hidden"
    );


    document.getElementById(
        "selectedCustomerId"
    ).textContent =
        valueOrNA(
            customer.customerid
        );


    // -----------------------------------------------------
    // CUSTOMER INFORMATION
    // -----------------------------------------------------

    document.getElementById(
        "detailCustomerId"
    ).textContent =
        valueOrNA(
            customer.customerid
        );


    document.getElementById(
        "detailGender"
    ).textContent =
        valueOrNA(
            customer.gender
        );


    document.getElementById(
        "detailSeniorCitizen"
    ).textContent =
        valueOrNA(
            customer.seniorcitizen
        );


    document.getElementById(
        "detailPartner"
    ).textContent =
        valueOrNA(
            customer.partner
        );


    document.getElementById(
        "detailDependents"
    ).textContent =
        valueOrNA(
            customer.dependents
        );


    document.getElementById(
        "detailTenure"
    ).textContent =
        customer.tenure != null
            ? `${customer.tenure} months`
            : "N/A";


    // -----------------------------------------------------
    // SERVICES
    // -----------------------------------------------------

    document.getElementById(
        "detailPhoneService"
    ).textContent =
        valueOrNA(
            customer.phoneservice
        );


    document.getElementById(
        "detailMultipleLines"
    ).textContent =
        valueOrNA(
            customer.multiplelines
        );


    document.getElementById(
        "detailInternetService"
    ).textContent =
        valueOrNA(
            customer.internetservice
        );


    document.getElementById(
        "detailOnlineSecurity"
    ).textContent =
        valueOrNA(
            customer.onlinesecurity
        );


    document.getElementById(
        "detailOnlineBackup"
    ).textContent =
        valueOrNA(
            customer.onlinebackup
        );


    document.getElementById(
        "detailDeviceProtection"
    ).textContent =
        valueOrNA(
            customer.deviceprotection
        );


    document.getElementById(
        "detailTechSupport"
    ).textContent =
        valueOrNA(
            customer.techsupport
        );


    document.getElementById(
        "detailStreamingTV"
    ).textContent =
        valueOrNA(
            customer.streamingtv
        );


    document.getElementById(
        "detailStreamingMovies"
    ).textContent =
        valueOrNA(
            customer.streamingmovies
        );


    // -----------------------------------------------------
    // BILLING & CONTRACT
    // -----------------------------------------------------

    document.getElementById(
        "detailContract"
    ).textContent =
        valueOrNA(
            customer.contract
        );


    document.getElementById(
        "detailPaperlessBilling"
    ).textContent =
        valueOrNA(
            customer.paperlessbilling
        );


    document.getElementById(
        "detailPaymentMethod"
    ).textContent =
        valueOrNA(
            customer.paymentmethod
        );


    document.getElementById(
        "detailMonthlyCharges"
    ).textContent =
        customer.monthlycharges != null
            ? currencyFormat(
                customer.monthlycharges
            )
            : "N/A";


    document.getElementById(
        "detailTotalCharges"
    ).textContent =
        customer.totalcharges != null
            ? currencyFormat(
                customer.totalcharges
            )
            : "N/A";


    document.getElementById(
        "detailTenureGroup"
    ).textContent =
        valueOrNA(
            customer.tenuregroup
        );


    document.getElementById(
        "detailTotalServices"
    ).textContent =
        valueOrNA(
            customer.totalservices
        );


    // -----------------------------------------------------
    // ML PREDICTION
    // -----------------------------------------------------

    const churnElement =
        document.getElementById(
            "detailChurn"
        );


    const churn =
        customer.churn;


    churnElement.textContent =
        valueOrNA(churn);


    churnElement.className =
        "";


    if (churn === "Yes") {

        churnElement.classList.add(
            "churn-yes"
        );

    } else if (churn === "No") {

        churnElement.classList.add(
            "churn-no"
        );
    }


    document.getElementById(
        "detailChurnProbability"
    ).textContent =

        customer.churn_probability != null
            ? percentFormat(
                customer.churn_probability
            )
            : "N/A";


    document.getElementById(
        "detailPredictedLtv"
    ).textContent =

        customer.predicted_ltv != null
            ? currencyFormat(
                customer.predicted_ltv
            )
            : "N/A";


    document.getElementById(
        "detailPredictionAt"
    ).textContent =
        dateFormat(
            customer.prediction_at
        );


    detailsSection.scrollIntoView({

        behavior: "smooth",

        block: "start"
    });
}


// =========================================================
// LOAD COMPLETE DASHBOARD
// =========================================================

async function loadDashboard() {

    await checkAPI();


    const operations = [

        loadSummary(),

        loadChurnOutcomeChart(),

        loadChurnRiskChart(),

        loadLtvChart(),

        loadGenderChart(),

        loadPartnerChart(),

        loadContractChart(),

        loadInternetChart(),

        loadTenureChart(),

        loadPaymentChart(),

        loadServicesChart(),

        loadPriorityCustomers(),

        loadCustomers()
    ];


    const results =
        await Promise.allSettled(
            operations
        );


    results.forEach(
        (result, index) => {

            if (
                result.status ===
                "rejected"
            ) {

                console.error(
                    `Dashboard component ${index + 1} failed:`,
                    result.reason
                );
            }
        }
    );
}


// =========================================================
// EVENT LISTENERS
// =========================================================

document
    .getElementById(
        "refreshButton"
    )
    .addEventListener(
        "click",
        loadDashboard
    );


document
    .getElementById(
        "searchButton"
    )
    .addEventListener(
        "click",
        () => {

            const customerId =
                document.getElementById(
                    "customerIdInput"
                ).value;


            searchCustomer(
                customerId
            );
        }
    );


document
    .getElementById(
        "customerIdInput"
    )
    .addEventListener(
        "keydown",
        event => {

            if (
                event.key ===
                "Enter"
            ) {

                const customerId =
                    document.getElementById(
                        "customerIdInput"
                    ).value;


                searchCustomer(
                    customerId
                );
            }
        }
    );


// =========================================================
// INITIAL LOAD
// =========================================================

window.addEventListener(
    "load",
    loadDashboard
);