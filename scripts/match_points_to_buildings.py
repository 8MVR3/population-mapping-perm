import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
import numpy as np
import os


def match_points_to_buildings(points_path, buildings_path, output_path, buffer_distance=0.0001):
    """
    Сопоставляет точки (дома с населением) с полигонами зданий OSM

    buffer_distance: радиус поиска в градусах (~10 метров на широте 58)
    """
    print("="*60)
    print("СОПОСТАВЛЕНИЕ ТОЧЕК С ЗДАНИЯМИ")
    print("="*60)

    # Загружаем точки с населением
    print(f"📥 Загружаем точки: {points_path}")
    points = gpd.read_file(points_path)
    print(f"   Загружено {len(points)} точек")

    # Загружаем здания OSM
    print(f"🏗️  Загружаем здания: {buildings_path}")
    buildings = gpd.read_file(buildings_path)
    print(f"   Загружено {len(buildings)} зданий")

    # Преобразуем в одну CRS для точных расчетов
    points = points.to_crs('EPSG:3857')  # Метрическая проекция
    buildings = buildings.to_crs('EPSG:3857')

    # Создаем буферы вокруг точек
    print("🔄 Создаем буферы вокруг точек...")
    points_buffered = points.copy()
    points_buffered['geometry'] = points_buffered.geometry.buffer(
        buffer_distance * 111000)  # ~10 метров

    # Пространственное соединение: какие здания попадают в буферы точек
    print("🔗 Выполняем пространственное соединение...")
    joined = gpd.sjoin(buildings, points_buffered,
                       how='inner', predicate='intersects')

    print(f"✅ Найдено {len(joined)} совпадений")

    if len(joined) == 0:
        print("❌ Нет совпадений! Увеличиваем радиус поиска...")
        # Пробуем увеличить радиус
        points_buffered['geometry'] = points.geometry.buffer(
            0.001 * 111000)  # ~100 метров
        joined = gpd.sjoin(buildings, points_buffered,
                           how='inner', predicate='intersects')
        print(f"   Теперь найдено: {len(joined)}")

    # Группируем: одно здание может соответствовать нескольким точкам
    # Берем среднее население для здания
    print("\n📊 Агрегируем данные...")

    if 'population' in joined.columns:
        # Группируем по зданиям, берем среднее население
        aggregated = joined.groupby(joined.index).agg({
            'population': 'mean',
            'geometry': 'first'
        })

        # Добавляем остальные колонки из зданий
        building_cols = [col for col in buildings.columns if col != 'geometry']
        for col in building_cols:
            if col in joined.columns:
                # Берем первое значение из группы
                aggregated[col] = joined.groupby(joined.index)[col].first()

        # Создаем GeoDataFrame
        train_data = gpd.GeoDataFrame(
            aggregated,
            geometry='geometry',
            crs='EPSG:3857'
        ).to_crs('EPSG:4326')  # Возвращаем в WGS84

        print(f"📈 Статистика по тренировочным данным:")
        print(f"   - Зданий с населением: {len(train_data)}")
        print(f"   - Всего населения: {train_data['population'].sum():.0f}")
        print(
            f"   - Среднее население на здание: {train_data['population'].mean():.2f}")

        # Сохраняем
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        train_data.to_file(output_path, driver='GeoJSON')
        print(f"\n💾 Сохранено в: {output_path}")

        return train_data
    else:
        print("❌ Нет колонки 'population' в данных")
        return None


def main():
    # Пример использования
    points_file = "data/zones/sverdlovsk_points.geojson"  # У нас есть население здесь
    buildings_file = "data/osm_test/buildings_osm.geojson"  # Наши тестовые здания
    output_file = "data/train_real/train_data.geojson"

    # Создаем директории
    os.makedirs("data/train_real", exist_ok=True)

    # Запускаем сопоставление
    train_data = match_points_to_buildings(
        points_file,
        buildings_file,
        output_file
    )

    # Также сохраняем как CSV для обучения
    if train_data is not None:
        csv_path = output_file.replace('.geojson', '.csv')
        # Извлекаем фичи из геометрии
        train_data['centroid_lon'] = train_data.geometry.centroid.x
        train_data['centroid_lat'] = train_data.geometry.centroid.y
        train_data['bld_area_m2'] = train_data.geometry.area

        # Сохраняем без геометрии
        df = train_data.drop(columns=['geometry'])
        df.to_csv(csv_path, index=False)
        print(f"💾 CSV сохранен: {csv_path}")


if __name__ == '__main__':
    main()
