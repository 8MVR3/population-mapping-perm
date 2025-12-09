import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon
import os


def create_simple_features(buildings_path, output_csv):
    """Создает простые фичи для теста"""

    print(f"📖 Читаем файл: {buildings_path}")

    # Читаем здания
    buildings = gpd.read_file(buildings_path)
    print(f"📊 Найдено зданий: {len(buildings)}")

    # Проверяем CRS, преобразуем если нужно
    if buildings.crs is None:
        buildings = buildings.set_crs('EPSG:4326')

    # Преобразуем в проекцию для расчета площади в метрах
    buildings_proj = buildings.to_crs('EPSG:3857')

    # Создаем DataFrame с фичами
    features = []

    for idx, row in buildings.iterrows():
        # Базовые фичи
        feat = {
            'building_id': row.get('osm_id', idx),
            'bld_area_m2': buildings_proj.iloc[idx].geometry.area,
            'bld_perimeter_m': buildings_proj.iloc[idx].geometry.length,
        }

        # Координаты центра
        centroid = row.geometry.centroid
        feat['centroid_lon'] = centroid.x
        feat['centroid_lat'] = centroid.y

        # Простые дополнительные фичи
        feat['area_to_perimeter_ratio'] = feat['bld_area_m2'] / \
            max(feat['bld_perimeter_m'], 0.001)
        feat['is_large'] = 1 if feat['bld_area_m2'] > 100 else 0

        # Информация из свойств OSM
        for prop in ['building:levels', 'levels', 'floor_count']:
            if prop in row:
                try:
                    feat['levels'] = float(row[prop])
                    break
                except:
                    pass

        features.append(feat)

    # Создаем DataFrame
    features_df = pd.DataFrame(features)

    # Сохраняем
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    features_df.to_csv(output_csv, index=False)
    print(f"✅ Сохранено {len(features_df)} записей в {output_csv}")

    return features_df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--buildings', required=True,
                        help='Путь к GeoJSON с зданиями')
    parser.add_argument('--out-csv', required=True, help='Выходной CSV файл')

    args = parser.parse_args()

    create_simple_features(args.buildings, args.out_csv)
