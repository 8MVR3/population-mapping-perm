#!/usr/bin/env python3
"""
make_training.py
Скрипт объединяет ваши XLSX с геоданными зданий и делает areal interpolation (distribute polygon population to buildings inside).
Требует: pandas, geopandas, shapely, openpyxl, click
Предполагается, что XLSX содержит таблицу с полигонами (или административными зонами) + population field.
Если в ваших файлах пока нет геометрии, вы можете предварительно загрузить шейп-файлы/geojson с границами.
"""

import logging
from pathlib import Path
import click
import geopandas as gpd
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--zones-geojson", default="data/zones/zones.geojson", help="Zones with population (polygons) and a 'population' column")
@click.option("--bld-geojson", default="data/osm/buildings_osm.geojson", help="Buildings geojson")
@click.option("--out-train-csv", default="data/train/train_buildings_population.csv")
def main(zones_geojson, bld_geojson, out_train_csv):
    # Load zones (must have population column)
    zones = gpd.read_file(zones_geojson)
    if "population" not in zones.columns:
        logger.error("Zones geojson must have 'population' column.")
        return

    bld = gpd.read_file(bld_geojson)

    # Ensure CRS match
    if zones.crs != bld.crs:
        bld = bld.to_crs(zones.crs)

    # Spatial join: which building inside which zone
    bld["bld_area"] = bld.geometry.area
    joined = gpd.sjoin(
        bld, zones[["population", "geometry"]], how="left", predicate="within")
    # For buildings not within any zone -> they will be ignored; alternatively could use nearest
    # compute areal interpolation: for each zone distribute population proportionally to building area (excluding uninhabited buildings later)
    # first, group by zone (index_right) to compute area sum
    grouped = joined.groupby("index_right").agg(
        {"bld_area": "sum", "population": "first"}).rename(columns={"bld_area": "total_area"})
    joined = joined.join(grouped, on="index_right")

    # compute building population estimate (area-weighted)
    joined["pop_area_est"] = (
        joined["bld_area"] / joined["total_area"]) * joined["population"]
    # replace NaN with 0 for outside buildings
    joined["pop_area_est"] = joined["pop_area_est"].fillna(0)

    # Prepare final training table: features (none yet) + pop_area_est
    # We'll keep building id (index), geometry, area, and pop_area_est
    out = joined[["bld_area", "pop_area_est", "geometry"]].copy()
    out = out.rename(columns={"pop_area_est": "population"})
    out.to_file(out_train_csv.replace(".csv", ".geojson"), driver="GeoJSON")
    # CSV without geometry for training
    df = pd.DataFrame(out.drop(columns=["geometry"]))
    df.to_csv(out_train_csv, index=False)

    logger.info(
        f"Saved training CSV to {out_train_csv} and geojson to {out_train_csv.replace('.csv', '.geojson')}")


if __name__ == "__main__":
    main()
