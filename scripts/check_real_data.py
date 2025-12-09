import geopandas as gpd
import pandas as pd
import os

print("="*60)
print("ПРОВЕРКА РЕАЛЬНЫХ ДАННЫХ")
print("="*60)

# 1. Проверяем данные Свердловской области
print("\n📍 СВЕРДЛОВСКАЯ ОБЛАСТЬ:")
sverdlovsk_path = "data/zones/sverdlovsk_points.geojson"
if os.path.exists(sverdlovsk_path):
    gdf = gpd.read_file(sverdlovsk_path)
    print(f"   Всего точек: {len(gdf)}")

    # Проверяем координаты
    print(
        f"   Широта (LAT): min={gdf['LAT'].min():.3f}, max={gdf['LAT'].max():.3f}")
    print(
        f"   Долгота (LON): min={gdf['LON'].min():.3f}, max={gdf['LON'].max():.3f}")

    # Проверяем население
    if 'population' in gdf.columns:
        print(
            f"   Население: total={gdf['population'].sum():.0f}, mean={gdf['population'].mean():.2f}")

    # Проверяем странные координаты (0,0)
    zero_coords = gdf[(gdf['LAT'] == 0) | (gdf['LON'] == 0)]
    print(f"   Точек с координатами 0: {len(zero_coords)}")

    # Показываем первые 5 точек
    print("\n   Первые 5 точек:")
    for i in range(min(5, len(gdf))):
        print(
            f"     {i+1}: LAT={gdf.iloc[i]['LAT']:.3f}, LON={gdf.iloc[i]['LON']:.3f}, pop={gdf.iloc[i].get('population', 'N/A')}")

# 2. Проверяем данные Пермского края
print("\n📍 ПЕРМСКИЙ КРАЙ:")
perm_path = "data/zones/perm_points.geojson"
if os.path.exists(perm_path):
    gdf = gpd.read_file(perm_path)
    print(f"   Всего точек: {len(gdf)}")

    # Проверяем координаты
    print(
        f"   Широта (Latitude): min={gdf['Latitude'].min():.3f}, max={gdf['Latitude'].max():.3f}")
    print(
        f"   Долгота (Longitude): min={gdf['Longitude'].min():.3f}, max={gdf['Longitude'].max():.3f}")

    # Проверяем население
    if 'population' in gdf.columns:
        print(
            f"   Население: total={gdf['population'].sum():.0f}, mean={gdf['population'].mean():.2f}")

    # Показываем первые 5 точек
    print("\n   Первые 5 точек:")
    for i in range(min(5, len(gdf))):
        print(
            f"     {i+1}: LAT={gdf.iloc[i]['Latitude']:.3f}, LON={gdf.iloc[i]['Longitude']:.3f}, pop={gdf.iloc[i].get('population', 'N/A')}")
