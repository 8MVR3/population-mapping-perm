#!/usr/bin/env python3
"""
train.py
Тренировка RandomForest регрессора на feature CSV + target population.
Зависимости: scikit-learn, pandas, joblib, click
"""

import logging
from pathlib import Path
import click
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--features-csv", default="data/features/building_features.csv")
@click.option("--train-csv", default="data/train/train_buildings_population.csv")
@click.option("--model-out", default="models/rf_pop_model.joblib")
@click.option("--test-size", default=0.2)
def main(features_csv, train_csv, model_out, test_size):
    feat_path = Path(features_csv)
    train_path = Path(train_csv)
    model_path = Path(model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    # Load
    feats = pd.read_csv(features_csv)
    train = pd.read_csv(train_csv)

    # merge on index order - ensure same number / alignment; better to have an id column, but here we assume order
    # safer: if both have geometry files, better to do spatial join; we assume featurize used same building order
    df = pd.concat([feats.reset_index(drop=True), train.reset_index(
        drop=True)], axis=1).dropna(subset=["population"])

    X = df.drop(columns=["population"])
    y = df["population"].astype(float)

    # Simple cleaning: drop non-numeric
    X = X.select_dtypes(include=[float, int])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42)

    rf = RandomForestRegressor(n_estimators=200, n_jobs=-1, random_state=42)
    logger.info("Training RandomForestRegressor...")
    rf.fit(X_train, y_train)

    # eval
    y_pred = rf.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    logger.info(f"Test MAE: {mae:.2f}, RMSE: {rmse:.2f}")

    # save model and feature columns
    joblib.dump({"model": rf, "features": X.columns.tolist()}, model_path)
    logger.info(f"Saved model to {model_path}")


if __name__ == "__main__":
    main()
