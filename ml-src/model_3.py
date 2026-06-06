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



