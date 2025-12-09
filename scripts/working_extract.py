#!/usr/bin/env python3
# РАБОЧИЙ скрипт загрузки OSM с настройками для медленных соединений
import requests
import osmnx as ox
import geopandas as gpd
from pathlib import Path
import time

print("=" * 60)
print("РАБОЧИЙ загрузчик OSM с настройками таймаутов")
print("=" * 60)

# КРИТИЧЕСКИ ВАЖНЫЕ НАСТРОЙКИ для России
ox.settings.timeout = 600  # 10 минут вместо 180
ox.settings.memory = 1024 * 8  # 8 ГБ памяти
ox.settings.use_cache = True
ox.settings.log_console = True  # Видим прогресс

# Создаем папку
Path("data/working_osm").mkdir(parents=True, exist_ok=True)

# ОЧЕНЬ МАЛЕНЬКАЯ область для теста
north, south, east, west = 58.0140, 58.0135, 56.2290, 56.2285
print(f"Мини-область: {north}, {south}, {east}, {west}")
print(f"Размер: ~{(north-south)*111}км × {(east-west)*111}км")

print("\n" + "=" * 40)
print("1. ТЕСТ: Одно здание (должно работать!)")

try:
    start = time.time()

    # ПРАВИЛЬНЫЙ синтаксис для OSMnx 2.0.7
    # bbox КАК КОРТЕЖ, tags как именованный параметр
    buildings = ox.features_from_bbox(
        bbox=(north, south, east, west),  # ← КОРТЕЖ!
        tags={"building": True}
    )

    elapsed = time.time() - start
    print(f"   ✅ УСПЕХ за {elapsed:.1f} сек!")
    print(f"   Зданий: {len(buildings)}")

    # Быстрое сохранение
    if len(buildings) > 0:
        buildings.to_file(
            "data/working_osm/test_building.geojson", driver="GeoJSON")
        print("   Сохранено: data/working_osm/test_building.geojson")

        # Показать что загрузили
        print("\n   Пример здания:")
        first = buildings.iloc[0]
        print(f"   - Тип: {first.get('building', 'нет данных')}")
        print(f"   - Площадь: {first.geometry.area:.0f} кв.м")

except Exception as e:
    print(f"   ❌ ОШИБКА: {type(e).__name__}")
    print(f"   {e}")

print("\n" + "=" * 40)
print("2. Проверка доступа к серверам...")

# Тест доступности Overpass API
try:
    resp = requests.get("http://overpass-api.de/api/status", timeout=10)
    print(f"   Статус сервера: {resp.text[:100]}")
except Exception as e:
    print(f"   ❌ Нет доступа к Overpass API: {e}")
    print("   🔧 Попробуйте включить VPN!")
    print("   Рекомендуемые страны: Германия, Финляндия, Нидерланды")

print("\n" + "=" * 40)
print("Следующие шаги:")
print("1. Если УСПЕХ — увеличим область")
print("2. Если ОШИБКА — нужен VPN или зеркало")
print("=" * 60)
