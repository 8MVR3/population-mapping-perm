#!/usr/bin/env python3
# Финальный тест для определения правильного синтаксиса
import osmnx as ox
import geopandas as gpd

print(f"OSMnx версия: {ox.__version__}")
print("=" * 50)

# Координаты микро-области в Перми
north, south, east, west = 58.014, 58.013, 56.229, 56.228

print("Тест 1: Четыре позиционных аргумента (самый вероятный вариант)")
try:
    gdf = ox.features_from_bbox(
        north, south, east, west,  # ← 4 аргумента БЕЗ именования
        tags={"building": True}
    )
    print(f"✅ УСПЕХ! Загружено зданий: {len(gdf)}")
    if len(gdf) > 0:
        gdf.to_file("test_success.geojson", driver="GeoJSON")
        print("Сохранено в test_success.geojson")
except Exception as e:
    print(f"❌ Ошибка: {type(e).__name__}: {e}")

print("\n" + "=" * 50)
print("Тест 2: bbox как кортеж")
try:
    gdf = ox.features_from_bbox(
        bbox=(north, south, east, west),
        tags={"building": True}
    )
    print(f"✅ УСПЕХ! Загружено зданий: {len(gdf)}")
except Exception as e:
    print(f"❌ Ошибка: {type(e).__name__}: {e}")

print("\n" + "=" * 50)
print("Проверка функции graph_from_bbox:")
try:
    G = ox.graph_from_bbox(north, south, east, west, network_type="drive")
    print(f"✅ УСПЕХ! Загружен граф дорог")
except Exception as e:
    print(f"❌ Ошибка: {type(e).__name__}: {e}")
