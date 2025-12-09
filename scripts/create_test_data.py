#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create_test_data.py
Создает тестовые данные для всего пайплайна оценки населения
"""

import geopandas as gpd
from shapely.geometry import Polygon, LineString
import pandas as pd
import numpy as np
from pathlib import Path

print('=' * 60)
print('СОЗДАНИЕ ТЕСТОВЫХ ДАННЫХ ДЛЯ ВСЕГО ПАЙПЛАЙНА')
print('=' * 60)

# Создаем все нужные папки
Path('data/osm').mkdir(parents=True, exist_ok=True)
Path('data/features').mkdir(parents=True, exist_ok=True)
Path('data/train').mkdir(parents=True, exist_ok=True)
Path('data/zones').mkdir(parents=True, exist_ok=True)
Path('data/predictions').mkdir(parents=True, exist_ok=True)
Path('models').mkdir(parents=True, exist_ok=True)

# --- 1. ЗДАНИЯ (1000 объектов) ---
print('1. Создаем 1000 тестовых зданий...')
buildings_data = []
for i in range(1000):
    # Случайные координаты в районе Перми
    lon = 56.2 + np.random.random() * 0.1
    lat = 58.0 + np.random.random() * 0.1

    buildings_data.append({
        'id': i,
        'geometry': Polygon([
            (lon, lat),
            (lon + 0.001, lat),
            (lon + 0.001, lat + 0.001),
            (lon, lat + 0.001)
        ]),
        'building': np.random.choice(['residential', 'house', 'apartments'], p=[0.7, 0.2, 0.1]),
        'area': 50 + np.random.randint(200),
        'height': np.random.randint(1, 10)
    })

buildings_gdf = gpd.GeoDataFrame(buildings_data, crs='EPSG:4326')
buildings_gdf.to_file('data/osm/buildings_osm.geojson', driver='GeoJSON')
print(
    f'   ✅ Сохранено: data/osm/buildings_osm.geojson ({len(buildings_gdf)} объектов)')

# --- 2. ДОРОГИ (упрощенные) ---
print('\n2. Создаем упрощенные дороги...')
roads_data = []
for i in range(50):
    lon = 56.2 + np.random.random() * 0.1
    lat = 58.0 + np.random.random() * 0.1

    roads_data.append({
        'id': i,
        'geometry': LineString([(lon, lat), (lon + 0.002, lat + 0.001)]),
        'highway': 'residential',
        'length': 100 + np.random.randint(100)
    })

roads_gdf = gpd.GeoDataFrame(roads_data, crs='EPSG:4326')
roads_gdf.to_file('data/osm/roads_edges.geojson', driver='GeoJSON')
print(
    f'   ✅ Сохранено: data/osm/roads_edges.geojson ({len(roads_gdf)} сегментов)')

# --- 3. POI (точки интереса) ---
print('\n3. Создаем POI...')
poi_data = []
poi_types = ['school', 'shop', 'cafe', 'hospital', 'park']
for i in range(100):
    lon = 56.2 + np.random.random() * 0.1
    lat = 58.0 + np.random.random() * 0.1

    poi_data.append({
        'id': i,
        'geometry': Polygon([(lon, lat), (lon+0.0002, lat), (lon+0.0002, lat+0.0002), (lon, lat+0.0002)]),
        'amenity': np.random.choice(poi_types),
        'name': f'POI_{i}'
    })

poi_gdf = gpd.GeoDataFrame(poi_data, crs='EPSG:4326')
poi_gdf.to_file('data/osm/pois_osm.geojson', driver='GeoJSON')
print(f'   ✅ Сохранено: data/osm/pois_osm.geojson ({len(poi_gdf)} POI)')

# --- 4. ЗОНЫ с населением (для тренировки) ---
print('\n4. Создаем зоны с населением...')
zones_data = []
for i in range(5):
    zones_data.append({
        'zone_id': i,
        'name': f'Район_{chr(65+i)}',
        'population': [5000, 7500, 10000, 3000, 6000][i],
        'geometry': Polygon([
            (56.2 + (i % 3)*0.05, 58.0 + (i//3)*0.05),
            (56.2 + (i % 3)*0.05 + 0.03, 58.0 + (i//3)*0.05),
            (56.2 + (i % 3)*0.05 + 0.03, 58.0 + (i//3)*0.05 + 0.03),
            (56.2 + (i % 3)*0.05, 58.0 + (i//3)*0.05 + 0.03)
        ])
    })

zones_gdf = gpd.GeoDataFrame(zones_data, crs='EPSG:4326')
zones_gdf.to_file('data/zones/zones.geojson', driver='GeoJSON')
print(f'   ✅ Сохранено: data/zones/zones.geojson ({len(zones_gdf)} зон)')
print('   Население по зонам:')
for _, row in zones_gdf.iterrows():
    print(f'     - {row["name"]}: {row["population"]} чел.')

print('\n' + '=' * 60)
print('ВСЕ ТЕСТОВЫЕ ДАННЫЕ СОЗДАНЫ!')
print('Теперь можно запускать пайплайн:')
print('1. python featurize.py')
print('2. python make_training.py')
print('3. python train.py')
print('4. python predict.py')
print('=' * 60)
