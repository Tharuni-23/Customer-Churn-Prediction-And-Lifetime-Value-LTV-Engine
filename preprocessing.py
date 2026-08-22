# ============================================================
# preprocessing.py
#
# FIT SIDE:
#   build_preprocessing_package(raw_df)
#
# APPLY SIDE:
#   transform(raw_df, package)
#
# The same preprocessing package is used for prediction.
# ============================================================

import numpy as np
import pandas as pd
import joblib


# ============================================================
# 1. CANONICAL COLUMNS
# ============================================================

CANONICAL_COLUMNS = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn",
    "TenureGroup",
    "TotalServices"
]


# ============================================================
# 2. BINARY COLUMNS
# ============================================================

BINARY_COLUMNS = [
    "Partner",
    "Dependents",
    "PhoneService",
    "PaperlessBilling"
]


# ============================================================
# 3. SERVICE COLUMNS
# ============================================================

SERVICE_COLUMNS = [
    "MultipleLines",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies"
]


# ============================================================
# 4. SERVICE COLLAPSE MAPPING
# ============================================================

SERVICE_COLLAPSE_MAPPING = {
    "No internet service": "No",
    "No phone service": "No"
}


# ============================================================
# 5. TENURE MAPPING
# ============================================================

TENURE_MAPPING = {
    "0-1 Year": 0,
    "1-2 Years": 1,
    "2-4 Years": 2,
    "4-6 Years": 3
}


# ============================================================
# 6. NUMERIC COLUMNS
# ============================================================

NUMERIC_MODEL_COLUMNS = [
    "SeniorCitizen",
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "TenureGroup",
    "TotalServices"
]


# These are specifically the charge columns where invalid
# values are converted to NaN and then filled with 0.
NUMERIC_CHARGE_COLUMNS = [
    "MonthlyCharges",
    "TotalCharges"
]


# ============================================================
# 7. ONE-HOT COLUMNS
# ============================================================

ONE_HOT_COLUMNS = [
    "InternetService",
    "Contract",
    "PaymentMethod"
]


# ============================================================
# 8. STAGE PRINTER
# ============================================================

def _stage(n, total, title):
    print(f"\n[Stage {n}/{total}] {title}")
    print("-" * (14 + len(title)))


# ============================================================
# 9. NORMALIZE COLUMN NAMES
# ============================================================

def normalize_columns(raw_df):

    raw_df = raw_df.copy()

    # Remove spaces around column names
    raw_df = raw_df.rename(
        columns=lambda c: c.strip()
    )

    # Map lowercase column names to actual names
    lower_to_actual = {
        c.lower(): c
        for c in raw_df.columns
    }

    rename_map = {}
    missing = []

    for col in CANONICAL_COLUMNS:

        key = col.lower()

        if key in lower_to_actual:
            actual_name = lower_to_actual[key]

            if actual_name != col:
                rename_map[actual_name] = col

        else:
            missing.append(col)

    if missing:

        raise ValueError(
            f"Missing columns "
            f"(checked case-insensitively): {missing}\n"
            f"Actual columns found: "
            f"{raw_df.columns.tolist()}"
        )

    return raw_df.rename(
        columns=rename_map
    )


# ============================================================
# 10. BUILD PREPROCESSING PACKAGE
# ============================================================

def build_preprocessing_package(
    raw_df,
    save_path="preprocessing_package.pkl"
):

    total_stages = 9

    # --------------------------------------------------------
    # Stage 1
    # --------------------------------------------------------

    _stage(
        1,
        total_stages,
        "Verify & normalize columns"
    )

    original_columns = raw_df.columns.tolist()

    raw_df = normalize_columns(
        raw_df
    )

    renamed = [
        (o, n)
        for o, n
        in zip(
            original_columns,
            raw_df.columns.tolist()
        )
        if o != n
    ]

    print(
        f"Columns received     : "
        f"{len(original_columns)}"
    )

    print(
        f"Columns renamed      : "
        f"{len(renamed)}"
        +
        (
            f"  e.g. {renamed[:3]}"
            if renamed
            else " (already correctly cased)"
        )
    )

    print(
        "All required columns present "
        "(case-insensitive match)."
    )

    # --------------------------------------------------------
    # Remove ID and target
    # --------------------------------------------------------

    data = raw_df.drop(
        columns=[
            "customerID",
            "Churn"
        ]
    ).copy()

    print(
        "Dropped columns      : "
        "customerID, Churn "
        "(kept aside, not model features)"
    )

    print(
        f"Feature frame shape  : "
        f"{data.shape[0]} rows x "
        f"{data.shape[1]} columns"
    )

    # --------------------------------------------------------
    # Stage 2 - Gender
    # --------------------------------------------------------

    _stage(
        2,
        total_stages,
        "Encode gender (Male=1, Female=0)"
    )

    before_unique = (
        data["gender"]
        .unique()
        .tolist()
    )

    data["gender"] = data[
        "gender"
    ].map({
        "Male": 1,
        "Female": 0
    })

    nulls_created = (
        data["gender"]
        .isnull()
        .sum()
    )

    print(
        f"Values before        : "
        f"{before_unique}"
    )

    print(
        "Values after         : "
        f"{sorted(data['gender'].dropna().unique().tolist())}"
    )

    print(
        f"Unmapped -> NaN      : "
        f"{nulls_created}"
        +
        (
            "  <-- check for typos/"
            "unexpected categories"
            if nulls_created
            else " (clean)"
        )
    )

    # --------------------------------------------------------
    # Stage 3 - Binary
    # --------------------------------------------------------

    _stage(
        3,
        total_stages,
        "Encode binary Yes/No columns"
    )

    for col in BINARY_COLUMNS:

        before_counts = (
            data[col]
            .value_counts()
            .to_dict()
        )

        data[col] = data[col].map({
            "Yes": 1,
            "No": 0
        })

        print(
            f"  {col:<18}"
            f" Yes/No counts before: "
            f"{before_counts} -> now 0/1"
        )

    total_nulls = (
        data[BINARY_COLUMNS]
        .isnull()
        .sum()
        .sum()
    )

    print(
        f"Unmapped -> NaN "
        f"(all binary cols): "
        f"{total_nulls}"
        +
        (
            "  <-- investigate"
            if total_nulls
            else " (clean)"
        )
    )

    # --------------------------------------------------------
    # Stage 4 - Services
    # --------------------------------------------------------

    _stage(
        4,
        total_stages,
        "Encode service columns"
    )

    collapse_counts = {}

    for col in SERVICE_COLUMNS:

        collapse_counts[col] = (
            data[col]
            .isin(
                SERVICE_COLLAPSE_MAPPING.keys()
            )
            .sum()
        )

        data[col] = data[col].replace(
            SERVICE_COLLAPSE_MAPPING
        )

        data[col] = data[col].map({
            "Yes": 1,
            "No": 0
        })

    print(
        "Rows collapsed to 'No' "
        "per column:"
    )

    for col, n in collapse_counts.items():

        print(
            f"  {col:<18} "
            f"{n} rows collapsed"
        )

    total_nulls = (
        data[SERVICE_COLUMNS]
        .isnull()
        .sum()
        .sum()
    )

    print(
        f"Unmapped -> NaN "
        f"(all service cols): "
        f"{total_nulls}"
        +
        (
            "  <-- investigate"
            if total_nulls
            else " (clean)"
        )
    )

    # --------------------------------------------------------
    # Stage 5 - TenureGroup
    # --------------------------------------------------------

    _stage(
        5,
        total_stages,
        "Encode TenureGroup"
    )

    before_counts = (
        data["TenureGroup"]
        .value_counts()
        .to_dict()
    )

    data["TenureGroup"] = data[
        "TenureGroup"
    ].map(
        TENURE_MAPPING
    )

    print(
        f"Category counts before: "
        f"{before_counts}"
    )

    print(
        f"Mapping applied       : "
        f"{TENURE_MAPPING}"
    )

    nulls_created = (
        data["TenureGroup"]
        .isnull()
        .sum()
    )

    print(
        f"Unmapped -> NaN       : "
        f"{nulls_created}"
        +
        (
            "  <-- unexpected category found"
            if nulls_created
            else " (clean)"
        )
    )

    # --------------------------------------------------------
    # Stage 6 - Numeric conversion
    # --------------------------------------------------------

    _stage(
        6,
        total_stages,
        "Clean numeric columns"
    )

    for col in NUMERIC_MODEL_COLUMNS:

        print(
            f"  {col:<18}"
            f" dtype before: "
            f"{data[col].dtype}"
        )

        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

        print(
            f"  {col:<18}"
            f" dtype after : "
            f"{data[col].dtype}"
        )

    # --------------------------------------------------------
    # Fill numeric charge NaN with 0
    # --------------------------------------------------------

    charge_nulls = (
        data[NUMERIC_CHARGE_COLUMNS]
        .isnull()
        .sum()
    )

    charge_nulls = charge_nulls[
        charge_nulls > 0
    ]

    if len(charge_nulls) > 0:

        print(
            "Blank/invalid charge "
            "values found and filled with 0:"
        )

        print(
            charge_nulls.to_string()
        )

    else:

        print(
            "No blank/invalid charge "
            "values found."
        )

    data[
        NUMERIC_CHARGE_COLUMNS
    ] = data[
        NUMERIC_CHARGE_COLUMNS
    ].fillna(0)

    # --------------------------------------------------------
    # Any remaining numeric NaN?
    # --------------------------------------------------------

    numeric_nulls = (
        data[
            NUMERIC_MODEL_COLUMNS
        ]
        .isnull()
        .sum()
    )

    numeric_nulls = numeric_nulls[
        numeric_nulls > 0
    ]

    if len(numeric_nulls) > 0:

        raise ValueError(
            "Numeric columns contain "
            "unresolved NaN values:\n"
            f"{numeric_nulls}"
        )

    # --------------------------------------------------------
    # Stage 7 - One Hot Encoding
    # --------------------------------------------------------

    _stage(
        7,
        total_stages,
        "One-hot encode categorical columns"
    )

    cols_before = data.shape[1]

    for col in ONE_HOT_COLUMNS:

        n_categories = (
            data[col]
            .nunique()
        )

        print(
            f"  {col:<15}"
            f" {n_categories} categories "
            f"-> {n_categories - 1} "
            f"dummy columns"
        )

    data = pd.get_dummies(
        data,
        columns=ONE_HOT_COLUMNS,
        drop_first=True
    )

    bool_columns = (
        data
        .select_dtypes(
            include="bool"
        )
        .columns
    )

    data[
        bool_columns
    ] = data[
        bool_columns
    ].astype(int)

    print(
        "New dummy columns created:"
    )

    print(
        list(bool_columns)
    )

    print(
        f"Column count: "
        f"{cols_before} -> "
        f"{data.shape[1]}"
    )

    # --------------------------------------------------------
    # Explicit numeric conversion AFTER encoding
    # --------------------------------------------------------

    for col in data.columns:

        if data[col].dtype == "object":

            data[col] = pd.to_numeric(
                data[col],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Stage 8 - Integrity checks
    # --------------------------------------------------------

    _stage(
        8,
        total_stages,
        "Integrity checks"
    )

    missing_values = (
        data.isnull()
        .sum()
    )

    missing_values = missing_values[
        missing_values > 0
    ]

    if len(missing_values) > 0:

        print(
            "WARNING: Missing values found:"
        )

        print(
            missing_values.to_string()
        )

        raise ValueError(
            "Preprocessing produced "
            "missing values. Check "
            "the category mappings."
        )

    print(
        "Missing values check : "
        "PASS (0 found)"
    )

    non_numeric_columns = (
        data
        .select_dtypes(
            exclude=np.number
        )
        .columns
        .tolist()
    )

    if non_numeric_columns:

        raise ValueError(
            "Non-numeric columns remain: "
            f"{non_numeric_columns}"
        )

    print(
        f"Numeric type check   : "
        f"PASS (all {data.shape[1]} "
        f"columns numeric)"
    )

    infinite_values = np.isinf(
        data.to_numpy(
            dtype=float
        )
    ).sum()

    if infinite_values > 0:

        raise ValueError(
            "Infinite values "
            "detected in processed data."
        )

    print(
        f"Infinite value check : "
        f"PASS ({infinite_values} found)"
    )

    # --------------------------------------------------------
    # Stage 9 - Save package
    # --------------------------------------------------------

    _stage(
        9,
        total_stages,
        "Build & save preprocessing package"
    )

    feature_order = (
        data.columns.tolist()
    )

    preprocessing_package = {

        "feature_order":
            feature_order,

        "drop_columns":
            [
                "customerID",
                "Churn"
            ],

        "gender_mapping":
            {
                "Male": 1,
                "Female": 0
            },

        "binary_columns":
            BINARY_COLUMNS,

        "binary_mapping":
            {
                "Yes": 1,
                "No": 0
            },

        "service_columns":
            SERVICE_COLUMNS,

        "service_collapse_mapping":
            SERVICE_COLLAPSE_MAPPING,

        "service_mapping":
            {
                "Yes": 1,
                "No": 0
            },

        "tenure_mapping":
            TENURE_MAPPING,

        "numeric_model_columns":
            NUMERIC_MODEL_COLUMNS,

        "numeric_charge_columns":
            NUMERIC_CHARGE_COLUMNS,

        "numeric_charge_fill_value":
            0,

        "one_hot_columns":
            ONE_HOT_COLUMNS,

        "drop_first":
            True
    }

    joblib.dump(
        preprocessing_package,
        save_path
    )

    print(
        f"\n{'=' * 50}"
    )

    print(
        "PREPROCESSING PACKAGE READY"
    )

    print(
        f"{'=' * 50}"
    )

    print(
        f"Rows processed   : "
        f"{data.shape[0]}"
    )

    print(
        f"Features produced: "
        f"{len(feature_order)}"
    )

    print(
        "Feature list     :"
    )

    for i, feature in enumerate(
        feature_order,
        start=1
    ):

        print(
            f"  {i:02d}. {feature}"
        )

    print(
        f"Saved to         : "
        f"{save_path}"
    )

    return (
        preprocessing_package,
        data
    )


# ============================================================
# 11. APPLY SAVED PACKAGE
# ============================================================

def transform(raw_df, package):

    # --------------------------------------------------------
    # Normalize column names
    # --------------------------------------------------------

    raw_df = normalize_columns(
        raw_df
    )

    # --------------------------------------------------------
    # Drop ID + target when present
    # --------------------------------------------------------

    drop_cols = [
        c
        for c in package["drop_columns"]
        if c in raw_df.columns
    ]

    data = raw_df.drop(
        columns=drop_cols
    ).copy()

    # --------------------------------------------------------
    # Gender
    # --------------------------------------------------------

    data["gender"] = (
        data["gender"]
        .map(
            package["gender_mapping"]
        )
    )

    # --------------------------------------------------------
    # Binary
    # --------------------------------------------------------

    for col in package[
        "binary_columns"
    ]:

        data[col] = (
            data[col]
            .map(
                package[
                    "binary_mapping"
                ]
            )
        )

    # --------------------------------------------------------
    # Services
    # --------------------------------------------------------

    for col in package[
        "service_columns"
    ]:

        data[col] = (
            data[col]
            .replace(
                package[
                    "service_collapse_mapping"
                ]
            )
        )

        data[col] = (
            data[col]
            .map(
                package[
                    "service_mapping"
                ]
            )
        )

    # --------------------------------------------------------
    # TenureGroup
    # --------------------------------------------------------

    data["TenureGroup"] = (
        data["TenureGroup"]
        .map(
            package[
                "tenure_mapping"
            ]
        )
    )

    # --------------------------------------------------------
    # Convert ALL expected numeric columns
    # --------------------------------------------------------

    for col in package[
        "numeric_model_columns"
    ]:

        if col in data.columns:

            data[col] = pd.to_numeric(
                data[col],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Fill charge NaN
    # --------------------------------------------------------

    charge_columns = package[
        "numeric_charge_columns"
    ]

    for col in charge_columns:

        if col in data.columns:

            data[col] = pd.to_numeric(
                data[col],
                errors="coerce"
            )

    data[
        charge_columns
    ] = data[
        charge_columns
    ].fillna(
        package[
            "numeric_charge_fill_value"
        ]
    )

    # --------------------------------------------------------
    # One-hot encoding
    # --------------------------------------------------------

    data = pd.get_dummies(
        data,
        columns=package[
            "one_hot_columns"
        ],
        drop_first=package[
            "drop_first"
        ]
    )

    # --------------------------------------------------------
    # Boolean → integer
    # --------------------------------------------------------

    bool_columns = (
        data
        .select_dtypes(
            include="bool"
        )
        .columns
    )

    data[
        bool_columns
    ] = data[
        bool_columns
    ].astype(int)

    # --------------------------------------------------------
    # Explicit numeric conversion
    # --------------------------------------------------------

    for col in data.columns:

        if data[col].dtype == "object":

            data[col] = pd.to_numeric(
                data[col],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Check for missing values
    # --------------------------------------------------------

    missing_values = (
        data.isnull()
        .sum()
    )

    missing_values = missing_values[
        missing_values > 0
    ]

    if len(missing_values) > 0:

        raise ValueError(
            "Prediction preprocessing "
            "created missing values:\n"
            f"{missing_values}"
        )

    # --------------------------------------------------------
    # Reorder to EXACT training order
    # --------------------------------------------------------

    data = data.reindex(
        columns=package[
            "feature_order"
        ],
        fill_value=0
    )

    # --------------------------------------------------------
    # Final numeric dtype enforcement
    # --------------------------------------------------------

    data = data.astype(
        np.float32
    )

    return data


# ============================================================
# 12. DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    import database as db

    engine = db.get_engine()

    raw_df = db.fetch_all_customers(
        engine
    )

    build_preprocessing_package(
        raw_df
    )