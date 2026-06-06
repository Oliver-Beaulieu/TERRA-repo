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