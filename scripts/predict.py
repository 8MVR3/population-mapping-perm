#!/usr/bin/env python3
"""
predict.py
На вход: buildings geojson (same schema как при featurize), модель joblib
Выход: geojson с колонкой pred_population
"""

import logging
from pathlib import Path
import click
import geopandas as gpd
import pandas as pd
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--bld-features-geojson", default="data/features/building_features.geojson")
@click.option("--model-joblib", default="models/rf_pop_model.joblib")
@click.option("--out-geojson", default="data/predictions/buildings_with_pred_pop.geojson")
def main(bld_features_geojson, model_joblib, out_geojson):
    bld = gpd.read_file(bld_features_geojson)
    model_data = joblib.load(model_joblib)
    model = model_data["model"]
    feat_cols = model_data["features"]

    # select features
    X = bld[feat_cols].select_dtypes(include=['number']).fillna(0)

    preds = model.predict(X)
    bld["pred_population"] = preds
    outp = Path(out_geojson)
    outp.parent.mkdir(parents=True, exist_ok=True)
    bld.to_file(outp, driver="GeoJSON")
    logger.info(f"Saved predictions to {outp}")


if __name__ == "__main__":
    main()
