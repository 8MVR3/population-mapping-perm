#!/usr/bin/env python3
# Простейший тест OSMnx
import osmnx as ox
print(f"OSMnx version: {ox.__version__}")

# Микро-область (одно здание)
bbox = (58.0139, 58.0138, 56.2290, 56.2289)
print("Тестируем загрузку...")

try:
    # Пробуем загрузить 1 здание
    gdf = ox.features_from_bbox(
        north=bbox[0], south=bbox[1],
        east=bbox[2], west=bbox[3],
        tags={"building": True}
    )
    print(f"✅ Успех! Загружено зданий: {len(gdf)}")
    if len(gdf) > 0:
        gdf.to_file("test_building.geojson", driver="GeoJSON")
        print("Сохранено в test_building.geojson")
except Exception as e:
    print(f"❌ Ошибка: {type(e).__name__}: {e}")
    print("Проблема с доступом к серверам OSM")
