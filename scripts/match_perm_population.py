import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np
import os

print("="*60)
print("СОПОСТАВЛЕНИЕ НАСЕЛЕНИЯ ПЕРМСКОГО КРАЯ С OSM ЗДАНИЯМИ")
print("="*60)

# 1. Загружаем точки населения
print("📥 Загружаем точки населения Пермского края...")
points = gpd.read_file("data/zones/perm_points.geojson")
print(f"✅ Загружено {len(points)} точек")

# 2. Загружаем OSM здания
print("🏗️ Загружаем OSM здания...")
buildings = gpd.read_file("data/osm_real/buildings_osm.geojson")
print(f"✅ Загружено {len(buildings)} зданий")

# 3. Проверяем координаты
print("\n📍 Координаты точек населения:")
print(
    f"  Широта: {points.geometry.y.min():.3f} - {points.geometry.y.max():.3f}")
print(
    f"  Долгота: {points.geometry.x.min():.3f} - {points.geometry.x.max():.3f}")

print("📍 Координаты OSM зданий:")
print(
    f"  Широта: {buildings.geometry.centroid.y.min():.3f} - {buildings.geometry.centroid.y.max():.3f}")
print(
    f"  Долгота: {buildings.geometry.centroid.x.min():.3f} - {buildings.geometry.centroid.x.max():.3f}")

# 4. Сопоставляем каждую точку с ближайшим зданием
print("\n🔗 Сопоставляем точки с ближайшими зданиями...")

# Убедимся, что в одной проекции (для точного измерения расстояний)
# Используем проекцию UTM для региона
points_utm = points.to_crs('EPSG:32640')  # UTM zone 40N для Перми
buildings_utm = buildings.to_crs('EPSG:32640')

matched_data = []

for idx, point in points_utm.iterrows():
    # Вычисляем расстояние до всех зданий
    distances = buildings_utm.distance(point.geometry)

    # Находим ближайшее здание
    min_distance = distances.min()
    closest_idx = distances.idxmin()
    closest_building = buildings_utm.loc[closest_idx]

    # Если расстояние меньше 500 метров, считаем совпадением
    if min_distance < 500:  # 500 метров
        matched_data.append({
            'point_id': idx,
            'building_id': closest_idx,
            'distance_m': min_distance,
            'population': point['ЧН_Расчет'],
            'lon': point.geometry.x,
            'lat': point.geometry.y,
            'building_type': closest_building.get('building', 'unknown'),
            'building_area': closest_building.geometry.area if hasattr(closest_building.geometry, 'area') else 0,
            'building_levels': closest_building.get('building:levels', 1)
        })

print(
    f"✅ Найдено {len(matched_data)} совпадений ({len(matched_data)/len(points)*100:.1f}% точек)")

# 5. Сохраняем результат
output_dir = "data/train_real"
os.makedirs(output_dir, exist_ok=True)

# Сохраняем как CSV для обучения
df_matched = pd.DataFrame(matched_data)
csv_path = os.path.join(output_dir, "perm_matched_training.csv")
df_matched.to_csv(csv_path, index=False)
print(f"💾 Сохранено в {csv_path}")

# 6. Создаем GeoJSON с сопоставленными зданиями и населением
matched_buildings = buildings_utm.loc[[
    m['building_id'] for m in matched_data]].copy()
matched_buildings['population'] = [m['population'] for m in matched_data]
matched_buildings = matched_buildings.to_crs('EPSG:4326')  # Возвращаем в WGS84

geojson_path = os.path.join(output_dir, "perm_matched_buildings.geojson")
matched_buildings.to_file(geojson_path, driver='GeoJSON')
print(f"🗺️  Создан GeoJSON с сопоставленными зданиями: {geojson_path}")

# 7. Статистика
print("\n📊 СТАТИСТИКА СОПОСТАВЛЕНИЯ:")
print(f"  Всего точек: {len(points)}")
print(f"  Сопоставлено: {len(matched_data)}")
print(f"  Процент сопоставления: {len(matched_data)/len(points)*100:.1f}%")
print(f"  Среднее население на здание: {df_matched['population'].mean():.1f}")
print(
    f"  Общее население в сопоставленных зданиях: {df_matched['population'].sum():,.0f}")
print(f"  Среднее расстояние: {df_matched['distance_m'].mean():.1f} м")
