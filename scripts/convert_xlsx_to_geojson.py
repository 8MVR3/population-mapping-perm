import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os


def convert_perm():
    """Конвертирует данные Пермского края"""
    print("📥 Читаем данные Пермского края...")
    df = pd.read_excel('data/Пермский край - Население.xlsx')

    # Создаем геометрию из координат
    geometry = [Point(lon, lat)
                for lon, lat in zip(df['Longitude'], df['Latitude'])]

    # Создаем GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df,
        geometry=geometry,
        crs='EPSG:4326'
    )

    # Переименовываем колонку с населением (если она есть)
    if 'ЧН_Расчет' in gdf.columns:
        gdf = gdf.rename(columns={'ЧН_Расчет': 'population'})

    # Сохраняем
    output_path = 'data/zones/perm_points.geojson'
    gdf.to_file(output_path, driver='GeoJSON')
    print(f"✅ Сохранено {len(gdf)} точек в {output_path}")

    # Статистика
    if 'population' in gdf.columns:
        print(f"📊 Всего населения: {gdf['population'].sum():.0f}")
        print(f"📊 Среднее на точку: {gdf['population'].mean():.2f}")

    return gdf


def convert_sverdlovsk():
    """Конвертирует данные Свердловской области"""
    print("\n📥 Читаем данные Свердловской области...")
    df = pd.read_excel('data/Свердловская область - Население.xlsx')

    # Создаем геометрию из координат
    geometry = [Point(lon, lat) for lon, lat in zip(df['LON'], df['LAT'])]

    # Создаем GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df,
        geometry=geometry,
        crs='EPSG:4326'
    )

    # Переименовываем колонку с населением
    if 'INHAB' in gdf.columns:
        gdf = gdf.rename(columns={'INHAB': 'population'})

    # Сохраняем
    output_path = 'data/zones/sverdlovsk_points.geojson'
    gdf.to_file(output_path, driver='GeoJSON')
    print(f"✅ Сохранено {len(gdf)} точек в {output_path}")

    # Статистика
    if 'population' in gdf.columns:
        print(f"📊 Всего населения: {gdf['population'].sum():.0f}")
        print(f"📊 Среднее на точку: {gdf['population'].mean():.2f}")
        print(f"📊 Максимальное: {gdf['population'].max():.0f}")

    return gdf


def main():
    os.makedirs('data/zones', exist_ok=True)

    # Конвертируем оба файла
    perm_gdf = convert_perm()
    sverdlovsk_gdf = convert_sverdlovsk()

    # Сводка
    print("\n" + "="*60)
    print("📈 ИТОГОВАЯ СВОДКА")
    print("="*60)

    print(f"\n📍 Пермский край:")
    print(f"   - Точки: {len(perm_gdf)}")
    print(
        f"   - Население: {perm_gdf['population'].sum() if 'population' in perm_gdf.columns else 'Нет данных'}")

    print(f"\n📍 Свердловская область:")
    print(f"   - Точки: {len(sverdlovsk_gdf)}")
    print(
        f"   - Население: {sverdlovsk_gdf['population'].sum() if 'population' in sverdlovsk_gdf.columns else 'Нет данных'}")


if __name__ == '__main__':
    main()
