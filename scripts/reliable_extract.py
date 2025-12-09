#!/usr/bin/env python3
# Надежный загрузчик с альтернативными серверами
import osmnx as ox
import geopandas as gpd
from pathlib import Path
import time

print("=" * 60)
print("Надежный загрузчик OSM с альтернативными серверами")
print("=" * 60)

# 1. ПЕРЕКЛЮЧАЕМСЯ НА АЛЬТЕРНАТИВНЫЙ СЕРВЕР
ox.settings.overpass_url = "https://overpass.kumi.systems/api/interpreter"
# или другой вариант:
# ox.settings.overpass_url = "https://overpass.nchc.org.tw/api/interpreter"

# 2. УВЕЛИЧИВАЕМ ТАЙМАУТЫ
ox.settings.timeout = 300  # 5 минут
ox.settings.memory = 1024 * 10  # 10 ГБ

# 3. ОЧЕНЬ МАЛЕНЬКАЯ ОБЛАСТЬ для теста
north, south, east, west = 58.01396, 58.01394, 56.22901, 56.22899
print(f"Супер-малая область: {north}, {south}, {east}, {west}")
print(f"Размер: ~{(north-south)*111*1000:.1f}м × {(east-west)*111*1000:.1f}м")

# Создаем папку
Path("data/reliable_osm").mkdir(parents=True, exist_ok=True)

print("\n" + "=" * 40)
print("ТЕСТ 1: Одно здание с альтернативным сервером")

try:
    start = time.time()

    # ПРАВИЛЬНЫЙ СИНТАКСИС (мы его уже определили)
    buildings = ox.features_from_bbox(
        bbox=(north, south, east, west),
        tags={"building": True}
    )

    elapsed = time.time() - start
    print(f"✅ УСПЕХ за {elapsed:.1f} секунд!")
    print(f"   Загружено зданий: {len(buildings)}")

    if len(buildings) > 0:
        buildings.to_file(
            "data/reliable_osm/buildings.geojson", driver="GeoJSON")
        print(f"   Сохранено в: data/reliable_osm/buildings.geojson")

        # Быстрый анализ
        print(f"\n   Анализ данных:")
        print(
            f"   - Типы зданий: {buildings['building'].unique()[:5] if 'building' in buildings.columns else 'Нет данных'}")
        print(
            f"   - Площадь самого большого: {buildings.geometry.area.max():.0f} кв.м")

except Exception as e:
    print(f"❌ ОШИБКА с альтернативным сервером: {type(e).__name__}")
    print(f"   {e}")
    print("\n   Пробуем вернуться к основному серверу...")
    ox.settings.overpass_url = "https://overpass-api.de/api/interpreter"

    try:
        buildings = ox.features_from_bbox(
            bbox=(north, south, east, west),
            tags={"building": True}
        )
        print(f"   ✅ Основной сервер сработал!")
    except Exception as e2:
        print(f"   ❌ Оба сервера не работают: {e2}")

print("\n" + "=" * 40)
print("Создаем УПРОЩЕННЫЙ extract_osm.py для вас:")

# Создаем исправленную версию extract_osm.py
correct_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ИСПРАВЛЕННЫЙ extract_osm.py
Правильный синтаксис для OSMnx 2.0.7
"""

import logging
from pathlib import Path
import click
import osmnx as ox
import geopandas as gpd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Используем альтернативный сервер для надежности
ox.settings.overpass_url = "https://overpass.kumi.systems/api/interpreter"
ox.settings.timeout = 600  # 10 минут
ox.settings.use_cache = True
ox.settings.log_console = False


@click.command()
@click.option("--place", default=None, help="Название места (например, 'Perm, Russia')")
@click.option("--north", type=float, default=None)
@click.option("--south", type=float, default=None)
@click.option("--east", type=float, default=None)
@click.option("--west", type=float, default=None)
@click.option("--out-dir", default="data/osm", help="Выходная папка")
def main(place, north, south, east, west, out_dir):

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # ---------- РЕЖИМ ПО НАЗВАНИЮ МЕСТА ----------
    if place:
        logger.info(f"Загружаем данные для: {place}")
        gdf_buildings = ox.features_from_place(place, tags={"building": True})
        G = ox.graph_from_place(place, network_type="drive")
        gdf_pois = ox.features_from_place(
            place, tags={"amenity": True, "shop": True, "leisure": True}
        )

    # ---------- РЕЖИМ ПО BBOX ----------
    else:
        assert None not in (north, south, east, west), "Укажите bbox или название места"
        logger.info(f"Загружаем данные для bbox: {(north, south, east, west)}")
        
        # ПРАВИЛЬНЫЙ СИНТАКСИС для OSMnx 2.0.7
        bbox_tuple = (north, south, east, west)
        
        gdf_buildings = ox.features_from_bbox(
            bbox=bbox_tuple,  # ← КОРТЕЖ как именованный параметр
            tags={"building": True}
        )
        
        G = ox.graph_from_bbox(
            north=north, south=south, east=east, west=west,
            network_type="drive"
        )
        
        gdf_pois = ox.features_from_bbox(
            bbox=bbox_tuple,
            tags={"amenity": True, "shop": True, "leisure": True}
        )

    # ---------- СОХРАНЕНИЕ ----------
    _, edges = ox.graph_to_gdfs(G, nodes=True, edges=True,
                                node_geometry=False, fill_edge_geometry=True)

    bld_file = out / "buildings_osm.geojson"
    edges_file = out / "roads_edges.geojson"
    pois_file = out / "pois_osm.geojson"

    logger.info(f"Сохраняем здания: {bld_file}")
    gdf_buildings.to_file(bld_file, driver="GeoJSON")

    logger.info(f"Сохраняем дороги: {edges_file}")
    edges.to_file(edges_file, driver="GeoJSON")

    logger.info(f"Сохраняем POI: {pois_file}")
    gdf_pois.to_file(pois_file, driver="GeoJSON")

    logger.info("✅ Загрузка завершена успешно!")


if __name__ == "__main__":
    main()
'''

# Сохраняем исправленный файл
with open("extract_osm_fixed.py", "w", encoding="utf-8") as f:
    f.write(correct_code)

print("✅ Создан файл: extract_osm_fixed.py")
print("\nИнструкция по использованию:")
print("1. python reliable_extract.py    # тест альтернативного сервера")
print("2. python extract_osm_fixed.py --north 58.02 --south 57.98 --east 56.30 --west 56.20 --out-dir data/osm")
print("\n" + "=" * 60)
