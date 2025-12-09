#!/usr/bin/env python3
# Тестовый скрипт для проверки OSMnx (версия 2.0.7)
import osmnx as ox
import geopandas as gpd

print(f"OSMnx version: {ox.__version__}")

# Микро-область (одно здание) - координаты Перми
north, south, east, west = 58.0139, 58.0138, 56.2290, 56.2289
print(f"Тестируем загрузку для bbox: {north}, {south}, {east}, {west}")

try:
    # ВАЖНО: В OSMnx 2.x используем bbox как КОРТЕЖ, без именованных параметров
    gdf = ox.features_from_bbox(
        bbox=(north, south, east, west),  # ← Ключевое изменение!
        tags={"building": True}
    )

    print(f"✅ Успех! Загружено зданий: {len(gdf)}")

    if len(gdf) > 0:
        # Сохраняем результат для проверки
        gdf.to_file("test_building.geojson", driver="GeoJSON")
        print("✅ Сохранено в test_building.geojson")

        # Показываем информацию о первом здании
        print("\nПервое здание в данных:")
        print(gdf.iloc[0][['geometry', 'building']]
              if 'building' in gdf.columns else gdf.iloc[0])

except TypeError as e:
    print(f"❌ Ошибка TypeError: {e}")
    print("\nВозможные варианты вызова features_from_bbox:")
    print("1. bbox=(север, юг, восток, запад)")
    print("2. north=..., south=..., east=..., west=... (иногда работает)")
except Exception as e:
    print(f"❌ Другая ошибка: {type(e).__name__}: {e}")
    print("Проблема с доступом к серверам OSM или сетевым соединением")
