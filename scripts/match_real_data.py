import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import os


def main():
    print("="*60)
    print("СОПОСТАВЛЕНИЕ РЕАЛЬНЫХ ДАННЫХ")
    print("="*60)

    # 1. Загружаем реальные точки с населением (Свердловская область)
    print("📥 Загружаем точки с населением...")
    points_path = "data/zones/sverdlovsk_points.geojson"
    points = gpd.read_file(points_path)
    print(f"   Загружено {len(points)} точек")

    # 2. Создаем тестовые здания В ТОМ ЖЕ РАЙОНЕ что и точки
    print("\n📍 Анализируем координаты точек...")
    print(f"   Широта: {points['LAT'].min():.3f} - {points['LAT'].max():.3f}")
    print(f"   Долгота: {points['LON'].min():.3f} - {points['LON'].max():.3f}")

    # Берем средние координаты для теста
    avg_lat = points['LAT'].mean()
    avg_lon = points['LON'].mean()
    print(f"\n📍 Средние координаты: {avg_lon:.3f}, {avg_lat:.3f}")

    # 3. Создаем тестовые здания рядом с этими координатами
    print("\n🏗️ Создаем тестовые здания...")
    test_buildings = []

    # Создаем 5 тестовых зданий вокруг средней точки
    for i in range(5):
        # Случайное смещение от средней точки (до 0.01 градуса ~ 1 км)
        import random
        lon_offset = random.uniform(-0.005, 0.005)
        lat_offset = random.uniform(-0.005, 0.005)

        lon = avg_lon + lon_offset
        lat = avg_lat + lat_offset

        # Создаем квадратное здание 100x100 метров
        from shapely.geometry import Polygon
        size = 0.001  # ~100 метров
        building = {
            'type': 'Feature',
            'properties': {
                'osm_id': i + 1,
                'name': f'Test Building {i+1}',
                'building': 'yes',
                'building:levels': random.randint(1, 9)
            },
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[
                    [lon - size/2, lat - size/2],
                    [lon + size/2, lat - size/2],
                    [lon + size/2, lat + size/2],
                    [lon - size/2, lat + size/2],
                    [lon - size/2, lat - size/2]
                ]]
            }
        }
        test_buildings.append(building)

    # Сохраняем тестовые здания
    import json
    buildings_path = "data/osm_real/test_buildings.geojson"
    os.makedirs(os.path.dirname(buildings_path), exist_ok=True)

    with open(buildings_path, 'w') as f:
        json.dump({'type': 'FeatureCollection', 'features': test_buildings}, f)

    print(
        f"✅ Создано {len(test_buildings)} тестовых зданий в {buildings_path}")

    # 4. Теперь сопоставляем
    print("\n🔗 Сопоставляем точки с зданиями...")

    # Загружаем созданные здания
    buildings = gpd.read_file(buildings_path)

    # Преобразуем в одну проекцию
    points_proj = points.to_crs('EPSG:3857')
    buildings_proj = buildings.to_crs('EPSG:3857')

    # Создаем буферы вокруг точек (50 метров)
    points_buffered = points_proj.copy()
    points_buffered['geometry'] = points_proj.geometry.buffer(50)

    # Пространственный join
    joined = gpd.sjoin(buildings_proj, points_buffered,
                       how='inner', predicate='intersects')

    print(f"✅ Найдено {len(joined)} совпадений")

    if len(joined) > 0:
        # Группируем по зданиям
        aggregated = joined.groupby(joined.index).agg({
            'population': 'mean',
            'geometry': 'first'
        })

        # Создаем тренировочные данные
        train_data = gpd.GeoDataFrame(
            aggregated,
            geometry='geometry',
            crs='EPSG:3857'
        ).to_crs('EPSG:4326')

        # Добавляем координаты центра
        train_data['centroid_lon'] = train_data.geometry.centroid.x
        train_data['centroid_lat'] = train_data.geometry.centroid.y
        train_data['bld_area_m2'] = train_data.geometry.area

        # Сохраняем
        train_geojson_path = "data/train_real/train_data.geojson"
        train_csv_path = "data/train_real/train_data.csv"

        os.makedirs(os.path.dirname(train_geojson_path), exist_ok=True)

        train_data.to_file(train_geojson_path, driver='GeoJSON')
        train_data.drop(columns=['geometry']).to_csv(
            train_csv_path, index=False)

        print(f"\n📊 Статистика:")
        print(f"   - Зданий с населением: {len(train_data)}")
        print(f"   - Всего населения: {train_data['population'].sum():.0f}")
        print(f"   - Среднее на здание: {train_data['population'].mean():.2f}")
        print(f"\n💾 Сохранено:")
        print(f"   - GeoJSON: {train_geojson_path}")
        print(f"   - CSV: {train_csv_path}")
    else:
        print("❌ Нет совпадений. Увеличиваем радиус поиска...")

        # Пробуем увеличить радиус
        points_buffered['geometry'] = points_proj.geometry.buffer(
            500)  # 500 метров
        joined = gpd.sjoin(buildings_proj, points_buffered,
                           how='inner', predicate='intersects')
        print(f"   Найдено с радиусом 500м: {len(joined)}")


if __name__ == '__main__':
    main()
