#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_training_simple.py
Упрощенный скрипт для создания тренировочных данных.
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
@click.option("--zones-geojson", default="data/zones/zones.geojson")
@click.option("--bld-geojson", default="data/features/building_features.geojson")
@click.option("--out-train-csv", default="data/train/train_buildings_population.csv")
def main(zones_geojson, bld_geojson, out_train_csv):
    # Загружаем данные
    zones = gpd.read_file(zones_geojson)
    buildings = gpd.read_file(bld_geojson)

    print("=" * 60)
    print("СОЗДАНИЕ ТРЕНИРОВОЧНЫХ ДАННЫХ")
    print("=" * 60)
    print(f"Зоны: {len(zones)} объектов")
    print(f"Здания: {len(buildings)} объектов")

    # Проверяем наличие колонки population
    if "population" not in zones.columns:
        logger.error("❌ В зонах нет колонки 'population'!")
        print("Доступные колонки в зонах:", list(zones.columns))
        return

    # Убедимся, что CRS совпадают
    if zones.crs != buildings.crs:
        buildings = buildings.to_crs(zones.crs)

    # Простая интерполяция: каждому зданию внутри зоны присваиваем часть населения
    # пропорционально площади здания

    # 1. Вычисляем площадь зданий в проекции зон
    buildings_proj = buildings.to_crs(zones.crs)
    buildings_proj["bld_area_m2"] = buildings_proj.geometry.area

    # 2. Пространственный join: какие здания в каких зонах
    joined = gpd.sjoin(
        buildings_proj[["geometry", "bld_area_m2"] +
                       list(buildings.columns.difference(["geometry"]))],
        zones[["geometry", "population"]],
        how="left",
        predicate="within"
    )

    print(f"Зданий внутри зон: {joined['population'].notna().sum()}")
    print(f"Зданий вне зон: {joined['population'].isna().sum()}")

    # 3. Для зданий внутри зон распределяем население пропорционально площади
    # Группируем по зонам
    for idx in joined[joined["population"].notna()].index_right.unique():
        zone_mask = joined["index_right"] == idx
        zone_population = joined.loc[zone_mask, "population"].iloc[0]
        zone_area = joined.loc[zone_mask, "bld_area_m2"].sum()

        if zone_area > 0:
            # Распределяем население пропорционально площади
            joined.loc[zone_mask, "assigned_population"] = (
                joined.loc[zone_mask, "bld_area_m2"] /
                zone_area * zone_population
            )

    # 4. Для зданий вне зон ставим 0
    joined["assigned_population"] = joined["assigned_population"].fillna(0)

    # 5. Подготовка финальной таблицы
    # Берем только числовые колонки из фич + население
    numeric_cols = joined.select_dtypes(include=[np.number]).columns
    # Убираем временные колонки
    cols_to_drop = ["index_right", "bld_area_m2", "population"]
    feature_cols = [
        c for c in numeric_cols if c not in cols_to_drop and c != "assigned_population"]

    train_data = joined[feature_cols + ["assigned_population"]].copy()
    train_data = train_data.rename(
        columns={"assigned_population": "population"})

    # 6. Сохраняем
    outp = Path(out_train_csv)
    outp.parent.mkdir(parents=True, exist_ok=True)

    # CSV для обучения
    train_data.to_csv(out_train_csv, index=False)

    # GeoJSON для визуализации
    joined_with_pop = buildings_proj.copy()
    joined_with_pop["population"] = joined["assigned_population"].values
    joined_with_pop.to_file(out_train_csv.replace(
        ".csv", ".geojson"), driver="GeoJSON")

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ:")
    print(f"✅ Сохранено тренировочных данных: {len(train_data)} строк")
    print(f"CSV: {out_train_csv}")
    print(f"GeoJSON: {out_train_csv.replace('.csv', '.geojson')}")
    print(f"Колонок (фичи + target): {len(train_data.columns)}")
    print(
        f"Общее население в данных: {train_data['population'].sum():.0f} чел.")
    print(f"Зданий с населением > 0: {(train_data['population'] > 0).sum()}")
    print("Первые 5 строк:")
    print(train_data.head())
    print("=" * 60)


if __name__ == "__main__":
    main()
