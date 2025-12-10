import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        description='Сопоставление точек с OSM зданиями')
    parser.add_argument(
        '--points', type=str, default='data/zones/perm_points.geojson', help='Файл с точками населения')
    parser.add_argument(
        '--osm', type=str, default='data/osm_real/buildings.geojson', help='Файл с OSM зданиями')
    parser.add_argument(
        '--output', type=str, default='data/train_real/matched.csv', help='Выходной CSV файл')
    parser.add_argument('--radius', type=float, default=100,
                        help='Радиус поиска в метрах')

    args = parser.parse_args()

    print("📥 Загружаем данные...")

    # Загружаем точки населения
    points_gdf = gpd.read_file(args.points)
    print(f"✅ Загружено {len(points_gdf)} точек")

    # Загружаем OSM здания
    buildings_gdf = gpd.read_file(args.osm)
    print(f"✅ Загружено {len(buildings_gdf)} зданий")

    # Переводим в одну проекцию (для точного измерения расстояний)
    # Используем проекцию, которая сохраняет расстояния
    crs_utm = 'EPSG:32640'  # UTM зона 40N для Перми

    points_utm = points_gdf.to_crs(crs_utm)
    buildings_utm = buildings_gdf.to_crs(crs_utm)

    print("🔗 Сопоставляем точки с зданиями...")

    matched_data = []

    # Для каждой точки ищем ближайшее здание
    for idx, point in points_utm.iterrows():
        # Создаем буфер вокруг точки
        buffer = point.geometry.buffer(args.radius)

        # Находим здания, которые попадают в буфер
        possible_buildings = buildings_utm[buildings_utm.geometry.intersects(
            buffer)]

        if len(possible_buildings) > 0:
            # Берем ближайшее здание
            distances = possible_buildings.distance(point.geometry)
            closest_idx = distances.idxmin()
            closest_building = buildings_utm.loc[closest_idx]

            # Сохраняем данные
            matched_data.append({
                'point_id': idx,
                'building_id': closest_idx,
                'population': point.get('INHAB') or point.get('ЧН_Расчет') or point.get('population', 0),
                'lon': point.geometry.x,
                'lat': point.geometry.y,
                'building_area': closest_building.get('area', 0),
                'building_type': closest_building.get('building', 'unknown')
            })

    print(
        f"✅ Найдено {len(matched_data)} совпадений ({len(matched_data)/len(points_gdf)*100:.1f}%)")

    # Сохраняем результат
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df_matched = pd.DataFrame(matched_data)
    df_matched.to_csv(args.output, index=False)
    print(f"💾 Результаты сохранены в {args.output}")


if __name__ == "__main__":
    main()
