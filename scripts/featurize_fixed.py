#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
featurize_fixed.py
Исправленная версия для работы с тестовыми данными.
Убраны сложные OSMnx вызовы, оставлены базовые фичи.
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
@click.option("--buildings", default="data/osm/buildings_osm.geojson")
@click.option("--pois", default="data/osm/pois_osm.geojson")
@click.option("--roads", default="data/osm/roads_edges.geojson")
@click.option("--out-csv", default="data/features/building_features.csv")
def main(buildings, pois, roads, out_csv):
    # Загружаем данные
    bld = gpd.read_file(buildings)

    # Проверяем, какие файлы существуют
    try:
        pois_gdf = gpd.read_file(pois)
        has_pois = True
    except:
        logger.warning(f"POI файл не найден: {pois}. Пропускаем POI фичи.")
        has_pois = False
        pois_gdf = None

    try:
        roads_gdf = gpd.read_file(roads)
        has_roads = True
    except:
        logger.warning(
            f"Дороги файл не найден: {roads}. Пропускаем дорожные фичи.")
        has_roads = False
        roads_gdf = None

    # Базовые фичи (всегда работают)
    if bld.crs is None:
        bld.set_crs(epsg=4326, inplace=True)

    # Проекция для метрических расчетов
    metric_crs = "EPSG:3857"
    bld_proj = bld.to_crs(metric_crs)

    # 1. Простые геометрические фичи
    bld["bld_area_m2"] = bld_proj.geometry.area
    bld["bld_perimeter_m"] = bld_proj.geometry.length
    bld["centroid_lon"] = bld.geometry.centroid.x
    bld["centroid_lat"] = bld.geometry.centroid.y

    # 2. Фичи из атрибутов (если есть)
    if "building" in bld.columns:
        bld["has_building_tag"] = bld["building"].notnull().astype(int)
        # Кодируем типы зданий
        building_types = pd.get_dummies(
            bld["building"].fillna("unknown"), prefix="bld_type")
        bld = pd.concat([bld, building_types], axis=1)
    else:
        bld["has_building_tag"] = 0

    if "area" in bld.columns:
        bld["area_numeric"] = pd.to_numeric(
            bld["area"], errors='coerce').fillna(0)
    else:
        bld["area_numeric"] = bld["bld_area_m2"]

    if "height" in bld.columns:
        bld["height_numeric"] = pd.to_numeric(
            bld["height"], errors='coerce').fillna(1)
    else:
        bld["height_numeric"] = 1

    # 3. Пространственные фичи (если есть POI)
    if has_pois and pois_gdf is not None:
        # Простой счетчик POI в буфере (упрощенная версия)
        pois_proj = pois_gdf.to_crs(metric_crs)
        bld_proj["centroid"] = bld_proj.geometry.centroid

        for r in [100, 250, 500]:  # метры
            try:
                # Создаем буферы вокруг центроидов
                buffers = bld_proj["centroid"].buffer(r)

                # Простой spatial join (без оптимизации для теста)
                count = []
                for buf in buffers:
                    # Считаем POI внутри буфера
                    in_buffer = pois_proj[pois_proj.intersects(buf)]
                    count.append(len(in_buffer))

                bld[f"pois_within_{r}m"] = count
            except Exception as e:
                logger.warning(f"Не удалось посчитать POI в радиусе {r}м: {e}")
                bld[f"pois_within_{r}m"] = 0
    else:
        # Заполняем нулями если нет POI
        for r in [100, 250, 500]:
            bld[f"pois_within_{r}m"] = 0

    # 4. Дорожные фичи (если есть дороги)
    if has_roads and roads_gdf is not None:
        try:
            roads_proj = roads_gdf.to_crs(metric_crs)
            bld_proj["centroid"] = bld_proj.geometry.centroid

            # Простой расчет длины дорог в буфере 250м
            road_lengths = []
            for centroid in bld_proj["centroid"]:
                buf = centroid.buffer(250)
                roads_in_buffer = roads_proj[roads_proj.intersects(buf)]
                if len(roads_in_buffer) > 0:
                    # Приблизительная длина
                    total_length = roads_in_buffer.geometry.length.sum()
                    road_lengths.append(total_length)
                else:
                    road_lengths.append(0)

            bld["roadlen_250m"] = road_lengths
        except Exception as e:
            logger.warning(f"Не удалось посчитать длину дорог: {e}")
            bld["roadlen_250m"] = 0
    else:
        bld["roadlen_250m"] = 0

    # 5. Плотность зданий (простая версия)
    try:
        densities = []
        for i, geom in enumerate(bld_proj.geometry):
            buf = geom.buffer(100)
            # Считаем сколько зданий в буфере (включая само здание)
            nearby = bld_proj[bld_proj.intersects(buf)]
            density = len(nearby) / (buf.area / 10000.0) if buf.area > 0 else 0
            densities.append(density)
        bld["bld_density_100m"] = densities
    except Exception as e:
        logger.warning(f"Не удалось посчитать плотность зданий: {e}")
        bld["bld_density_100m"] = 0

    # 6. Дополнительные фичи
    bld["area_to_perimeter_ratio"] = bld["bld_area_m2"] / \
        (bld["bld_perimeter_m"] + 1e-6)
    bld["volume_estimate"] = bld["bld_area_m2"] * bld["height_numeric"]

    # Сохраняем результат
    outp = Path(out_csv)
    outp.parent.mkdir(parents=True, exist_ok=True)

    # Выбираем только числовые колонки для CSV
    numeric_cols = bld.select_dtypes(include=[np.number]).columns
    df_to_save = bld[numeric_cols].copy()

    # Сохраняем CSV
    df_to_save.to_csv(out_csv, index=False)

    # Сохраняем GeoJSON с геометрией (для визуализации)
    geo_cols = list(numeric_cols) + ["geometry"]
    bld[geo_cols].to_file(str(outp).replace(
        ".csv", ".geojson"), driver="GeoJSON")

    logger.info(f"✅ Сохранено фичей: {len(bld)} объектов")
    logger.info(f"CSV: {out_csv} ({len(df_to_save.columns)} колонок)")
    logger.info(f"GeoJSON: {str(outp).replace('.csv', '.geojson')}")

    # Показываем статистику
    print("\n" + "=" * 50)
    print("СТАТИСТИКА ФИЧ:")
    print(f"Всего объектов: {len(bld)}")
    print(f"Колонок: {len(df_to_save.columns)}")
    print("Примерные колонки:")
    for col in list(df_to_save.columns)[:10]:  # первые 10 колонок
        print(f"  - {col}")
    if len(df_to_save.columns) > 10:
        print(f"  ... и еще {len(df_to_save.columns) - 10} колонок")
    print("=" * 50)


if __name__ == "__main__":
    main()
