import geopandas as gpd
import pandas as pd
import numpy as np
import os


def main():
    print("="*60)
    print("ФИЧЕИЗАЦИЯ РЕАЛЬНЫХ ДАННЫХ")
    print("="*60)

    # Загружаем тренировочные данные
    train_path = "data/train_real/train_data.geojson"
    if not os.path.exists(train_path):
        print(f"❌ Файл не найден: {train_path}")
        return

    print(f"📥 Загружаем данные: {train_path}")
    train_data = gpd.read_file(train_path)
    print(f"✅ Загружено {len(train_data)} зданий")

    # Создаем фичи
    print("\n🔧 Создаем фичи...")

    # Базовые фичи уже есть: centroid_lon, centroid_lat, bld_area_m2, population

    # Добавляем дополнительные фичи
    features = pd.DataFrame()

    # Основные фичи
    features['building_id'] = range(1, len(train_data) + 1)
    features['centroid_lon'] = train_data['centroid_lon']
    features['centroid_lat'] = train_data['centroid_lat']
    features['bld_area_m2'] = train_data['bld_area_m2']

    # Вычисляем периметр
    train_data_proj = train_data.to_crs('EPSG:3857')
    features['bld_perimeter_m'] = train_data_proj.geometry.length

    # Соотношение площадь/периметр
    features['area_to_perimeter_ratio'] = features['bld_area_m2'] / \
        (features['bld_perimeter_m'] + 0.001)

    # Признаки из свойств OSM
    if 'building:levels' in train_data.columns:
        features['levels'] = train_data['building:levels'].fillna(1)
    else:
        features['levels'] = 1

    # Целевая переменная
    features['population'] = train_data['population']

    # Сохраняем
    output_csv = "data/features_real/building_features.csv"
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    features.to_csv(output_csv, index=False)
    print(f"\n💾 Сохранено {len(features)} записей в {output_csv}")

    # Статистика
    print(f"\n📊 Статистика фичей:")
    for col in features.columns:
        if col != 'building_id':
            print(
                f"   {col}: min={features[col].min():.2f}, max={features[col].max():.2f}, mean={features[col].mean():.2f}")


if __name__ == '__main__':
    main()
