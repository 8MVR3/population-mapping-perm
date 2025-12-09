import geopandas as gpd
import pandas as pd
import numpy as np
import os
import json

print("="*60)
print("СОЗДАНИЕ РЕАЛИСТИЧНЫХ ТЕСТОВЫХ ДАННЫХ")
print("="*60)

# 1. Загружаем реальные данные для получения реалистичных координат
print("\n📥 Загружаем реальные данные для анализа...")
perm_path = "data/zones/perm_points.geojson"

if os.path.exists(perm_path):
    gdf = gpd.read_file(perm_path)

    # Берем реальные координаты из данных
    # Ищем подходящие координаты (не 0,0)
    valid_points = gdf[(gdf['Longitude'] > 56) & (gdf['Longitude'] < 57) &
                       (gdf['Latitude'] > 58) & (gdf['Latitude'] < 59)]

    if len(valid_points) > 0:
        # Берем первые 10 точек как основу
        base_points = valid_points.head(10)
        base_lon = base_points['Longitude'].mean()
        base_lat = base_points['Latitude'].mean()

        print(f"📍 Используем координаты из реальных данных:")
        print(f"   Центр: {base_lon:.4f}, {base_lat:.4f}")

        # 2. Создаем тестовые здания
        print("\n🏗️ Создаем тестовые здания...")
        buildings = []

        for i in range(20):
            # Случайное смещение от центра (до 0.02 градуса ~ 2 км)
            lon = base_lon + np.random.uniform(-0.01, 0.01)
            lat = base_lat + np.random.uniform(-0.01, 0.01)

            # Случайный размер здания (100-500 кв.м)
            size = np.random.uniform(0.0003, 0.0008)  # 30-80 метров

            building = {
                'type': 'Feature',
                'properties': {
                    'osm_id': i + 1,
                    'name': f'Test Building {i+1}',
                    'building': 'yes',
                    'building:levels': np.random.randint(1, 10)
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
            buildings.append(building)

        # Сохраняем здания
        buildings_path = "data/osm_real/realistic_buildings.geojson"
        os.makedirs(os.path.dirname(buildings_path), exist_ok=True)

        with open(buildings_path, 'w') as f:
            json.dump({'type': 'FeatureCollection', 'features': buildings}, f)

        print(f"✅ Создано {len(buildings)} тестовых зданий в {buildings_path}")

        # 3. Создаем тренировочные данные
        print("\n📊 Создаем тренировочные данные...")
        train_data = []

        for i, building in enumerate(buildings):
            props = building['properties']
            geom = building['geometry']

            # Вычисляем площадь (примерно)
            coords = geom['coordinates'][0]
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]

            # Простая аппроксимация площади
            width = max(lons) - min(lons)
            height = max(lats) - min(lats)
            area_m2 = width * height * 111000 * 111000  # грубое приближение

            # Население зависит от площади и этажности
            population = area_m2 * \
                props['building:levels'] * 0.01 + np.random.normal(0, 5)
            population = max(1, population)  # минимум 1 человек

            train_data.append({
                'building_id': props['osm_id'],
                'centroid_lon': np.mean(lons),
                'centroid_lat': np.mean(lats),
                'bld_area_m2': area_m2,
                'bld_perimeter_m': 2 * (width + height) * 111000,  # периметр
                'area_to_perimeter_ratio': area_m2 / (2 * (width + height) * 111000 + 0.001),
                'levels': props['building:levels'],
                'population': population
            })

        # Создаем DataFrame
        df = pd.DataFrame(train_data)

        # Сохраняем
        train_csv_path = "data/train_real/realistic_train_data.csv"
        os.makedirs(os.path.dirname(train_csv_path), exist_ok=True)

        df.to_csv(train_csv_path, index=False)
        print(f"✅ Создано {len(df)} тренировочных записей в {train_csv_path}")

        # Статистика
        print(f"\n📊 Статистика:")
        print(f"   - Средняя площадь: {df['bld_area_m2'].mean():.1f} м²")
        print(f"   - Среднее население: {df['population'].mean():.1f} чел.")
        print(f"   - Всего населения: {df['population'].sum():.0f} чел.")

        print("\n🚀 Запустите обучение:")
        print(
            f"python scripts/train_fixed.py --features-csv {train_csv_path} --train-csv {train_csv_path}")

    else:
        print("❌ Не найдено подходящих координат в данных Пермского края")
else:
    print("❌ Файл с данными Пермского края не найден")
