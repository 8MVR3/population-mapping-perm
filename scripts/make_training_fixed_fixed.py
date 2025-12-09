import geopandas as gpd
import pandas as pd
from shapely.geometry import shape
import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        description='Подготовка тренировочных данных (исправленная версия)')
    parser.add_argument('--zones-geojson', required=True,
                        help='GeoJSON с зонами и населением')
    parser.add_argument('--features-csv', required=True,
                        help='CSV с фичами зданий')
    parser.add_argument('--out-train-csv', required=True,
                        help='Выходной CSV с тренировочными данными')

    args = parser.parse_args()

    print("="*60)
    print("СОЗДАНИЕ ТРЕНИРОВОЧНЫХ ДАННЫХ (ИСПРАВЛЕННАЯ ВЕРСИЯ)")
    print("="*60)

    # 1. Загружаем зоны
    print(f"Загружаем зоны: {args.zones_geojson}")
    zones = gpd.read_file(args.zones_geojson)
    print(f"✅ Зоны: {len(zones)} объектов")

    # 2. Загружаем фичи зданий
    print(f"Загружаем фичи зданий: {args.features_csv}")
    buildings_features = pd.read_csv(args.features_csv)
    print(f"✅ Здания: {len(buildings_features)} объектов")

    # 3. Создаем GeoDataFrame из зданий
    # Нужно иметь геометрию зданий. Если её нет в CSV, мы не можем сделать пространственный join
    # Проверим, есть ли координаты центроидов
    if 'centroid_lon' in buildings_features.columns and 'centroid_lat' in buildings_features.columns:
        from shapely.geometry import Point
        geometry = [Point(xy) for xy in zip(
            buildings_features['centroid_lon'], buildings_features['centroid_lat'])]
        buildings = gpd.GeoDataFrame(
            buildings_features, geometry=geometry, crs='EPSG:4326')
    else:
        print("❌ В фичах зданий нет координат центроидов!")
        return

    # 4. Пространственный join: какие здания в каких зонах
    print("Выполняем пространственный join...")
    buildings_in_zones = gpd.sjoin(
        buildings, zones, how='inner', predicate='intersects')
    print(f"✅ Зданий внутри зон: {len(buildings_in_zones)}")

    if len(buildings_in_zones) == 0:
        print("❌ Нет зданий внутри зон! Проверьте координаты.")
        return

    # 5. Распределяем население по зданиям
    print("\nРаспределяем население по зданиям...")

    # Найдем колонку с населением в зонах
    pop_column = None
    for col in zones.columns:
        if 'population' in col.lower() or 'насел' in col.lower() or 'inhab' in col.lower():
            pop_column = col
            break

    if not pop_column:
        print("❌ Не найдена колонка с населением в зонах!")
        return

    # Распределение населения пропорционально площади
    training_data = []

    for zone_id in buildings_in_zones['index_right'].unique():
        zone_buildings = buildings_in_zones[buildings_in_zones['index_right'] == zone_id]
        zone_population = zones.loc[zone_id, pop_column]

        # Распределяем пропорционально площади
        total_area = zone_buildings['bld_area_m2'].sum()

        for idx, building in zone_buildings.iterrows():
            # Пропорциональное распределение
            if total_area > 0:
                pop_share = zone_population * \
                    (building['bld_area_m2'] / total_area)
            else:
                pop_share = 0

            # Создаем запись для обучения
            record = building.to_dict()
            record['population'] = pop_share
            training_data.append(record)

    # 6. Сохраняем данные
    train_df = pd.DataFrame(training_data)

    # Создаем директорию если нет
    os.makedirs(os.path.dirname(args.out_train_csv), exist_ok=True)

    # Сохраняем
    train_df.to_csv(args.out_train_csv, index=False)

    print("\n" + "="*60)
    print("✅ РЕЗУЛЬТАТЫ:")
    print(f"   Тренировочных данных: {len(train_df)} строк")
    print(f"   Колонок: {len(train_df.columns)}")
    print(
        f"   Общее население в данных: {train_df['population'].sum():.1f} чел.")
    print(f"   Файл сохранен: {args.out_train_csv}")
    print("="*60)


if __name__ == '__main__':
    main()
