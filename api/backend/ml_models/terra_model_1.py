#!/usr/bin/env python3
"""TERRA - Model 1 (Linear Regression)

Predicts asylum applications from climate and economic features.
Trained on 2010-2018 data, tested on 2019-2023 data.

Exposes training/testing via train_test_model() and real-time
prediction via predict(), which the REST API calls directly.
"""

import os
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

NUMERIC_FEATURES = [
    "year",
    "gdp_per_capita",
    "unemployment_rate",
    "population",
    "urban_pct",
    "temp_mean",
    "heatwave_days",
    "precip_total",
    "precip_days_heavy",
    "dry_days",
    "evapotrans_total",
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

    model = LinearRegression(n_estimators=300, learning_rate=0.05,
                                      max_depth=4, random_state=42)
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

def load_artifacts(model_path=MODEL_PATH):
    """Load the persisted model/scaler/features, training first if missing."""
    if not os.path.exists(model_path):
        print("No saved model found - training one first...\n")
        return train_test_model(model_path=model_path)
    return joblib.load(model_path)


def predict(user_inputs, model=None, scaler=None, features=None,
            model_path=MODEL_PATH):
    """Predict asylum applications for a single country/year.
    The model and scaler can be passed directly, or loaded from disk.
    """
    if model is None or scaler is None or features is None:
        artifacts = load_artifacts(model_path)
        model = artifacts["model"]
        scaler = artifacts["scaler"]
        features = artifacts["features"]

    row = pd.DataFrame([user_inputs])
    row = pd.get_dummies(row, columns=["country_code"])

    row = row.reindex(columns=features, fill_value=0)

    row_scaled = scaler.transform(row)
    log_prediction = model.predict(row_scaled)
    prediction = np.expm1(log_prediction)
    return float(prediction[0])


if __name__ == "__main__":
    train_test_model()
