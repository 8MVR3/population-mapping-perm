import geopandas as gpd

print("📊 Анализ OSM данных...")
buildings = gpd.read_file("data/osm_real/buildings_osm.geojson")
print(f"✅ Загружено {len(buildings)} зданий")
print("\n📋 Столбцы в данных:")
for col in buildings.columns:
    print(f"  - {col}")

print(f"\n📍 Пример здания:")
print(buildings.iloc[0][['geometry', 'building', 'amenity', 'name']])

print("\n📈 Статистика:")
print(f"  Уникальных типов зданий: {buildings['building'].nunique()}")
print(
    f"  Наиболее частые типы: {buildings['building'].value_counts().head(10).to_dict()}")
