import geopandas as gpd

print("📊 Проверка данных Пермского края...")
points = gpd.read_file("data/zones/perm_points.geojson")
print(f"✅ Загружено {len(points)} точек")

print("\n📋 Колонки:")
for col in points.columns:
    print(f"  - {col}: {points[col].dtype}")

print("\n🔍 Первые 5 строк:")
print(points.head())

print("\n📈 Статистика по числовым колонкам:")
numeric_cols = points.select_dtypes(include=['int64', 'float64']).columns
for col in numeric_cols:
    if col != 'geometry':
        print(
            f"  {col}: мин={points[col].min()}, макс={points[col].max()}, среднее={points[col].mean():.1f}")

# Попробуем найти колонку с населением
print("\n🔎 Поиск колонки с населением:")
for col in points.columns:
    if 'населен' in col.lower() or 'нас' in col.lower() or 'pop' in col.lower() or 'inh' in col.lower():
        print(
            f"  Возможно '{col}': значения от {points[col].min()} до {points[col].max()}")
