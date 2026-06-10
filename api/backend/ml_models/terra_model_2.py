#!/usr/bin/env python3
"""
TERRA - Model 2 (Multivariate Linear Regression)

Predicts three climate variables:
- heatwave_days
- precip_days_heavy
- dry_days

Uses economic + demographic + asylum features + country_code.
DB-backed: weights stored in model2_params / model2_scaler / model2_encoder.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

MODEL_PATH = os.path.join(ROOT_DIR, "outputs", "model_2_multi_linreg.joblib")

numeric_features = ["gdp_per_capita", "unemployment_rate", "population", "urban_pct", "asylum_applications"]
categorical_features = ["country_code"]

targets = ["heatwave_days", "precip_days_heavy", "dry_days"]


def load_data():
    """Load training data from the database."""
    from backend.db_connection import get_db
    query = """
        SELECT c.country_code, cyd.year,
               cyd.gdp_per_capita, cyd.unemployment_rate,
               cyd.population, cyd.urban_pct, cyd.asylum_applications,
               cyd.heatwave_days, cyd.precip_days_heavy, cyd.dry_days
        FROM country_year_data cyd
        JOIN country c ON cyd.country_id = c.country_id
        ORDER BY c.country_code, cyd.year
    """
    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    df = pd.DataFrame(rows)
    return df.dropna(subset=targets).copy()


def prepare_data(df):
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


def train_test_model(model_path=MODEL_PATH, test_size=0.20, random_state=42):
    df = load_data()
    X, y, model = prepare_data(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state)

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    r2   = r2_score(y_test, y_pred, multioutput="raw_values")
    rmse = np.sqrt(mean_squared_error(y_test, y_pred, multioutput="raw_values"))
    mae  = mean_absolute_error(y_test, y_pred, multioutput="raw_values")

    print("\n=== Model Performance ===")
    print("R²:", r2)
    print("RMSE:", rmse)
    print("MAE:", mae)

    artifacts = {
        "model": model,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "targets": targets,
        "metrics": {"r2": r2, "rmse": rmse, "mae": mae}
    }

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(artifacts, model_path)
    print(f"\nSaved model artifact to {model_path}")

    return artifacts


def store_params_in_db(artifacts, db=None):
    from backend.db_connection import get_db
    if db is None:
        db = get_db()

    model     = artifacts["model"]
    scaler    = model.named_steps["preprocessor"].transformers_[0][1]
    encoder   = model.named_steps["preprocessor"].transformers_[1][1]
    regressor = model.named_steps["regressor"]

    cursor = db.cursor()
    cursor.execute("SELECT COALESCE(MAX(sequence_number), 0) + 1 FROM model2_params")
    seq = cursor.fetchone()[0]

    cursor.execute(
        "INSERT INTO model2_params "
        "(sequence_number, target_names, numeric_feature_names, intercepts, coef_matrix) "
        "VALUES (%s, %s, %s, %s, %s)",
        (seq,
         json.dumps(targets),
         json.dumps(numeric_features),
         json.dumps([float(v) for v in regressor.intercept_]),
         json.dumps([[float(v) for v in row] for row in regressor.coef_])),
    )
    cursor.execute(
        "INSERT INTO model2_scaler (sequence_number, feature_means, feature_stds) "
        "VALUES (%s, %s, %s)",
        (seq,
         json.dumps([float(v) for v in scaler.mean_]),
         json.dumps([float(v) for v in scaler.scale_])),
    )
    cursor.execute(
        "INSERT INTO model2_encoder (sequence_number, categories) VALUES (%s, %s)",
        (seq, json.dumps([arr.tolist() for arr in encoder.categories_])),
    )
    db.commit()
    cursor.close()
    return seq


def _load_db_params():
    from backend.db_connection import get_db
    db = get_db()
    with db.cursor(dictionary=True) as cursor:
        cursor.execute(
            "SELECT numeric_feature_names, intercepts, coef_matrix "
            "FROM model2_params ORDER BY sequence_number DESC LIMIT 1"
        )
        p = cursor.fetchone()
        if p is None:
            raise ValueError("No model2 parameters in DB. Call POST /model2/train first.")
        cursor.execute(
            "SELECT feature_means, feature_stds FROM model2_scaler "
            "ORDER BY sequence_number DESC LIMIT 1"
        )
        s = cursor.fetchone()
        cursor.execute(
            "SELECT categories FROM model2_encoder ORDER BY sequence_number DESC LIMIT 1"
        )
        e = cursor.fetchone()

    return (
        json.loads(p["numeric_feature_names"]),
        np.array(json.loads(p["intercepts"]),  dtype=float),
        np.array(json.loads(p["coef_matrix"]), dtype=float),
        np.array(json.loads(s["feature_means"]), dtype=float),
        np.array(json.loads(s["feature_stds"]),  dtype=float),
        json.loads(e["categories"]),
    )


def predict(user_inputs):
    num_features, intercepts, coef_matrix, means, stds, categories = _load_db_params()

    row = pd.DataFrame([user_inputs])
    row = row.reindex(columns=numeric_features + categorical_features, fill_value=0)

    scaled = (row[num_features].values[0] - means) / stds
    country_cats = categories[0]
    one_hot = np.array([1.0 if c == str(user_inputs.get("country_code", "")) else 0.0
                        for c in country_cats])

    preds = intercepts + coef_matrix @ np.concatenate([scaled, one_hot])

    return {
        "heatwave_days_pred":     float(preds[0]),
        "precip_days_heavy_pred": float(preds[1]),
        "dry_days_pred":          float(preds[2]),
    }


if __name__ == "__main__":
    train_test_model()
