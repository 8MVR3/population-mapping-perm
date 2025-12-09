#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_training_fixed.py
Исправленная версия для создания тренировочных данных.
Использует здания с фичами (из featurize) и зоны с населением.
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
@click.option("--bld-features-geojson", default="data/features/building_features.geojson")
@click.option("--out-train-csv", default="data/train/train_buildings_population.csv")
def main(zones_geojson, bld_features_geojson, out_train_csv):
    print("=" * 60)
    print("СОЗДАНИЕ ТРЕНИРОВОЧНЫХ ДАННЫХ")
    print("=" * 60)

    # 1. Загружаем данные
    zones = gpd.read_file(zones_geojson)
    buildings = gpd.read_file(bld_features_geojson)

    print(f"Зоны: {len(zones)} объектов")
    print(f"Здания (с фичами): {len(buildings)} объектов")

    # Проверяем наличие population в зонах
    if "population" not in zones.columns:
        logger.error("❌ В зонах нет колонки 'population'!")
        print("Доступные колонки в зонах:", list(zones.columns))
        return

    # 2. Выравниваем CRS
    if zones.crs != buildings.crs:
        buildings = buildings.to_crs(zones.crs)
        print(f"Конвертировали CRS зданий к: {zones.crs}")

    # 3. Вычисляем площадь зданий (в проекции зон)
    buildings["bld_area_m2"] = buildings.geometry.area

    # 4. Пространственный join: какие здания в каких зонах
    print("\nВыполняем пространственный join...")
    joined = gpd.sjoin(
        buildings,
        zones[["geometry", "population"]],
        how="left",
        predicate="within"
    )

    buildings_in_zones = joined["index_right"].notna().sum()
    print(f"Зданий внутри зон: {buildings_in_zones}")
    print(f"Зданий вне зон: {len(joined) - buildings_in_zones}")

    # 5. Распределяем население по площади (areal interpolation)
    print("\nРаспределяем население по зданиям...")

    # Для зданий внутри зон
    if buildings_in_zones > 0:
        # Группируем по зонам и вычисляем общую площадь
        zone_stats = joined[joined["index_right"].notna()].groupby("index_right").agg({
            "bld_area_m2": "sum",
            "population": "first"
        }).rename(columns={"bld_area_m2": "total_area"})

        # Присоединяем общую площадь обратно
        joined = joined.join(zone_stats[["total_area"]], on="index_right")

        # Вычисляем население для каждого здания (пропорционально площади)
        joined["assigned_population"] = 0.0
        mask = joined["index_right"].notna()
        joined.loc[mask, "assigned_population"] = (
            joined.loc[mask, "bld_area_m2"] /
            joined.loc[mask, "total_area"] *
            joined.loc[mask, "population"]
        )
    else:
        joined["assigned_population"] = 0.0

    # Заменяем NaN на 0 (для зданий вне зон)
    joined["assigned_population"] = joined["assigned_population"].fillna(0)

    # 6. Подготавливаем финальную таблицу для обучения
    print("\nПодготавливаем данные для обучения...")

    # Выбираем только числовые колонки (фичи)
    numeric_cols = joined.select_dtypes(include=[np.number]).columns.tolist()

    # Убираем временные колонки
    cols_to_remove = ["index_right", "bld_area_m2", "population", "total_area"]
    feature_cols = [
        col for col in numeric_cols if col not in cols_to_remove and col != "assigned_population"]

    # Создаем DataFrame для обучения
    train_data = joined[feature_cols + ["assigned_population"]].copy()
    train_data = train_data.rename(
        columns={"assigned_population": "population"})

    # Убираем строки где все фичи NaN (если есть)
    train_data = train_data.dropna(how="all", subset=feature_cols)

    # 7. Сохраняем результаты
    outp = Path(out_train_csv)
    outp.parent.mkdir(parents=True, exist_ok=True)

    # CSV для обучения модели
    train_data.to_csv(out_train_csv, index=False)

    # GeoJSON для визуализации
    joined_vis = buildings.copy()
    joined_vis["population"] = joined["assigned_population"].values
    joined_vis.to_file(out_train_csv.replace(
        ".csv", ".geojson"), driver="GeoJSON")

    # 8. Выводим статистику
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ:")
    print(f"✅ Тренировочных данных: {len(train_data)} строк")
    print(f"✅ Колонок (фичи + target): {len(train_data.columns)}")
    print(f"   - Фичи: {len(feature_cols)}")
    print(f"   - Target: 1 (population)")
    print(
        f"✅ Общее население в данных: {train_data['population'].sum():.0f} чел.")
    print(f"✅ Зданий с населением > 0: {(train_data['population'] > 0).sum()}")
    print(
        f"✅ Среднее население на здание: {train_data['population'].mean():.2f}")
    print(f"\n📁 Файлы:")
    print(f"   CSV: {out_train_csv}")
    print(f"   GeoJSON: {out_train_csv.replace('.csv', '.geojson')}")

    print("\n📊 Пример данных (первые 3 строки):")
    print(train_data[["population"] + feature_cols[:3]].head(3))
    print("=" * 60)


if __name__ == "__main__":
    main()
