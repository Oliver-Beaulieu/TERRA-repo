#!/usr/bin/env python3
"""TERRA - Model 1 (Linear Regression)

Predicts asylum applications from climate and economic features.
Trained on 2010-2018 data, tested on 2019-2023 data.

DB-served pattern (same as model02): the fitted parameters live in the
database, not in code or a binary artifact:
  - model1_params : feature_names + beta_vals ([intercept, *coefs])
  - model1_scaler : feature_means + feature_stds (StandardScaler params)

predict() reads those at request time and reconstructs the prediction. To
retrain, call train_test_model() to refit, then store_params_in_db() to write
the new parameters (the admin "Train" route does exactly this). The joblib
dump in train_test_model() is kept only as an offline evaluation artifact.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# Relative path list
HERE = os.path.dirname(os.path.abspath(__file__))

# Go from api/backend/ml_models/terra_model_1.py back to the repo root
ROOT_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))

DATA_PATH = os.path.join(ROOT_DIR, "datasets", "processed", "merged_data.csv")
RESULTS_PATH = os.path.join(ROOT_DIR, "outputs", "results.csv")
MODEL_PATH = os.path.join(ROOT_DIR, "outputs", "model_1.joblib")

# End year of training
TRAIN_MAX_YEAR = 2018

# Start of testing year
TEST_MIN_YEAR = 2019

# NOTE: raw calendar `year` is deliberately NOT a model feature. The scaler is
# fit on 2010-2018 only, so feeding a future year (the webapp defaults to 2024)
# pushes it far outside the training range and the positive time-trend coef
# inflates predictions several-fold. `year` is still used to split train/test.
#
# Features dropped via iterative VIF (multicollinearity):
#   - precip_total (VIF 23.6) and evapotrans_total (VIF 13.2): redundant with
#     the other climate aggregates.
#   - population (VIF ~7986) and urban_pct (VIF ~338): collinear with country
#     identity (the country_code dummies). Dropping them tamed the worst
#     coefficient from 7.66 to 1.38 and improved test MAE.
NUMERIC_FEATURES = [
    "gdp_per_capita",
    "unemployment_rate",
    "temp_mean",
    "heatwave_days",
    "precip_days_heavy",
    "dry_days",
]

def load_data(path=DATA_PATH):
    """Load the merged dataset and drop rows with no target value."""
    df = pd.read_csv(path)
    df = df.dropna(subset=["asylum_applications"]).copy()
    df = df.sort_values(["country_code", "year"])
    return df


def prepare_data(df):
    """
    Returns the prepared DataFrame as full feature list.
    """

    df = df.copy()
    for col in NUMERIC_FEATURES:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())

    df = pd.get_dummies(df, columns=["country_code"], drop_first=True)
    country_cols = [c for c in df.columns if c.startswith("country_code_")]
    features = NUMERIC_FEATURES + country_cols

    df["log_asylum"] = np.log1p(df["asylum_applications"])
    return df, features

def train_test_model(data_path=DATA_PATH, results_path=RESULTS_PATH,
                     model_path=MODEL_PATH):
    """Train on <=2018, evaluate on >=2019.

    Returns a dict: fitted model, scaler, feature list, and metrics.
    """
    df = load_data(data_path)
    df, features = prepare_data(df)
    country_cols = [c for c in features if c.startswith("country_code_")]

    train = df[df["year"] <= TRAIN_MAX_YEAR]
    test = df[df["year"] >= TEST_MIN_YEAR]
    print(f"Train rows: {len(train)} | Test rows: {len(test)}")

    X_train, y_train = train[features], train["log_asylum"]
    X_test, y_test = test[features], test["log_asylum"]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)

    mse_log = mean_squared_error(y_test, y_pred)
    r2_log = r2_score(y_test, y_pred)
    y_pred_orig = np.expm1(y_pred)
    y_test_orig = np.expm1(y_test)
    mae_orig = mean_absolute_error(y_test_orig, y_pred_orig)

    print(f"MSE (log scale): {mse_log:.4f}")
    print(f"R²  (log scale): {r2_log:.4f}")
    print(f"MAE (original count scale): {mae_orig:,.0f}")

    results = test[["year"]].copy()
    results["country"] = (
        test[country_cols].idxmax(axis=1).str.replace("country_code_", "")
    )
    results["actual"] = y_test_orig.values
    results["predicted"] = y_pred_orig
    results["error"] = results["actual"] - results["predicted"]
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    results.to_csv(results_path, index=False)
    print(f"\nSaved test predictions to {results_path}")
    print("\nLargest absolute errors:")
    print(results.sort_values("error", key=abs, ascending=False).head(15))

    # Preserve artifacts so we don't need to retrain
    artifacts = {
        "model": model,
        "scaler": scaler,
        "features": features,
        "metrics": {"mse_log": mse_log, "r2_log": r2_log, "mae_orig": mae_orig},
    }
    joblib.dump(artifacts, model_path)
    print(f"\nSaved model artifact to {model_path}")

    return artifacts

def store_params_in_db(artifacts, db=None):
    """Persist a fitted model's parameters into model1_params / model1_scaler.

    Writes a new versioned row (sequence_number = max + 1) so predict() picks
    up the latest. Called by the admin retrain route after train_test_model().
    """
    from backend.db_connection import get_db
    if db is None:
        db = get_db()

    model, scaler, features = artifacts["model"], artifacts["scaler"], artifacts["features"]
    feature_names = json.dumps(list(features))
    beta_vals = json.dumps([float(model.intercept_)] + [float(c) for c in model.coef_])
    feature_means = json.dumps([float(x) for x in scaler.mean_])
    feature_stds = json.dumps([float(x) for x in scaler.scale_])

    cursor = db.cursor()
    cursor.execute("SELECT COALESCE(MAX(sequence_number), 0) + 1 FROM model1_params")
    seq = cursor.fetchone()[0]
    cursor.execute(
        "INSERT INTO model1_params (sequence_number, feature_names, beta_vals) "
        "VALUES (%s, %s, %s)",
        (seq, feature_names, beta_vals),
    )
    cursor.execute(
        "INSERT INTO model1_scaler (sequence_number, feature_means, feature_stds) "
        "VALUES (%s, %s, %s)",
        (seq, feature_means, feature_stds),
    )
    db.commit()
    cursor.close()
    return seq


def _load_db_params():
    """Fetch the latest beta vector + scaler params from the database."""
    from backend.db_connection import get_db
    db = get_db()
    with db.cursor(dictionary=True) as cursor:
        cursor.execute(
            "SELECT feature_names, beta_vals FROM model1_params "
            "ORDER BY sequence_number DESC LIMIT 1"
        )
        params_row = cursor.fetchone()
        if params_row is None:
            raise ValueError("No model1 parameters found in the database.")

        cursor.execute(
            "SELECT feature_means, feature_stds FROM model1_scaler "
            "ORDER BY sequence_number DESC LIMIT 1"
        )
        scaler_row = cursor.fetchone()
        if scaler_row is None:
            raise ValueError("No model1 scaler parameters found in the database.")

    feature_names = json.loads(params_row["feature_names"])
    beta = np.array(json.loads(params_row["beta_vals"]), dtype=float)
    means = np.array(json.loads(scaler_row["feature_means"]), dtype=float)
    stds = np.array(json.loads(scaler_row["feature_stds"]), dtype=float)
    return feature_names, beta, means, stds


def predict(user_inputs):
    """Predict asylum applications for a single country.

    Reads the fitted parameters from the database (model1_params /
    model1_scaler), reconstructs the standardized feature row, and applies
    log_pred = intercept + scaled_features . coefs, then expm1.
    """
    feature_names, beta, means, stds = _load_db_params()

    # Build the raw feature row and align it to the stored feature order.
    # Country becomes one-hot columns; the reference country (dropped at train
    # time) and any features the model no longer uses fall away on reindex.
    row = pd.DataFrame([user_inputs])
    row = pd.get_dummies(row, columns=["country_code"])
    row = row.reindex(columns=feature_names, fill_value=0)

    x = row.iloc[0].to_numpy(dtype=float)
    x_scaled = (x - means) / stds
    log_prediction = beta[0] + x_scaled @ beta[1:]
    return float(np.expm1(log_prediction))


if __name__ == "__main__":
    train_test_model()
