#!/usr/bin/env python3
"""
TERRA - Model 3 (Multivariate Linear Regression)

Predicts three climate variables:
- heatwave_days
- precip_days_heavy
- dry_days

Uses economic + demographic + asylum features + country_code.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# Paths
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "..", "datasets", "processed", "merged_data.csv")
MODEL_PATH = os.path.join(HERE, "..", "outputs", "model_3_multi_linreg.joblib")

# Feature definitions
numeric_features = ["gdp_per_capita", "unemployment_rate", "population", "urban_pct", "asylum_applications"]
categorical_features = ["country_code"]

targets = ["heatwave_days", "precip_days_heavy", "dry_days"]

def load_data(path=DATA_PATH):
    """Load the merged dataset"""
    df = pd.read_csv(path)
    df = df.dropna(subset=targets).copy()
    return df

def prepare_data(df):
    """Prepare features and targets"""
    df = df.copy()

    X = df[numeric_features + categorical_features]
    y = df[targets]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
        ]
    )

    model = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", LinearRegression())
    ])

    return X, y, model

def train_test_model(
    data_path=DATA_PATH,
    model_path=MODEL_PATH,
    test_size=0.20,
    random_state=42,
    ):
    """Train model"""
    df = load_data(data_path)
    X, y, model = prepare_data(df)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state)
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    r2 = r2_score(y_test, y_pred, multioutput="raw_values")
    rmse = np.sqrt(mean_squared_error(y_test, y_pred, multioutput="raw_values"))
    mae = mean_absolute_error(y_test, y_pred, multioutput="raw_values")

    print("\n=== Model Performance ===")
    print("R²:", r2)
    print("RMSE:", rmse)
    print("MAE:", mae)

    artifacts = {
        "model": model,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "targets": targets,
        "metrics": {
            "r2": r2,
            "rmse": rmse,
            "mae": mae
        }
    }
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(artifacts, model_path)
    print(f"\nSaved model artifact to {model_path}")

    return artifacts

def load_artifacts(model_path=MODEL_PATH):
    """Load model"""
    if not os.path.exists(model_path):
        print("No saved model found — training one now...\n")
        return train_test_model(model_path=model_path)
    return joblib.load(model_path)

def predict(user_inputs, model=None, model_path=MODEL_PATH):
    """Predict climate variables for a single row"""

    if model is None:
        artifacts = load_artifacts(model_path)
        model = artifacts["model"]

    row = pd.DataFrame([user_inputs])
    row = row.reindex(columns=numeric_features + categorical_features, fill_value=0)
    preds = model.predict(row)[0]

    return {
        "heatwave_days_pred": float(preds[0]),
        "precip_days_heavy_pred": float(preds[1]),
        "dry_days_pred": float(preds[2]),
    }

if __name__ == "__main__":
    train_test_model()
