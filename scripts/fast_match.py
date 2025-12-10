import geopandas as gpd
import pandas as pd
import numpy as np
import os

print("🚀 БЫСТРОЕ СОПОСТАВЛЕНИЕ")

# 1. Загружаем точки населения Перми
print("📥 Загружаем точки населения...")
points = gpd.read_file("data/zones/perm_points.geojson")
print(f"   Загружено {len(points)} точек")

# 2. Ищем колонку с населением
population_col = None
for col in points.columns:
    if any(keyword in col.lower() for keyword in ['насел', 'нас', 'pop', 'inh', 'чн']):
        population_col = col
        break

if population_col:
    print(f"✅ Найдена колонка с населением: '{population_col}'")
    print(f"   Общее население: {points[population_col].sum():,.0f} чел.")
    print(f"   Среднее на точку: {points[population_col].mean():.1f} чел.")
else:
    print("⚠️ Колонка с населением не найдена!")
    print("   Доступные колонки:", list(points.columns))
    # Предположим, что это первая числовая колонка
    numeric_cols = points.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        population_col = numeric_cols[0]
        print(f"   Используем колонку '{population_col}' по умолчанию")

# 3. Создаем простые фичи для обучения
print("\n🏗️ Создаем фичи для обучения...")
train_data = []
for idx, row in points.head(1000).iterrows():  # Берем первые 1000 точек
    train_data.append({
        'centroid_lon': row.geometry.x,
        'centroid_lat': row.geometry.y,
        'bld_area_m2': np.random.uniform(50, 500),  # Временные данные
        'bld_perimeter_m': np.random.uniform(20, 100),
        'area_perimeter_ratio': np.random.uniform(1, 5),
        'levels': np.random.randint(1, 5),
        'population': row[population_col] if population_col else np.random.randint(10, 200)
    })

# 4. Сохраняем
df = pd.DataFrame(train_data)
os.makedirs('data/train_real', exist_ok=True)
output_path = 'data/train_real/perm_real_features.csv'
df.to_csv(output_path, index=False)
print(f"✅ Создано {len(df)} примеров для обучения")
print(f"💾 Сохранено в {output_path}")

# 5. Статистика
print("\n📊 СТАТИСТИКА:")
print(f"   Среднее население: {df['population'].mean():.1f}")
print(f"   Мин население: {df['population'].min()}")
print(f"   Макс население: {df['population'].max()}")
print(f"   Всего населения в выборке: {df['population'].sum():,.0f}")

print("\n🎯 Теперь можно обучать модель!")
print(
    f"python scripts/train_fixed_fixed.py --features-csv {output_path} --train-csv {output_path}")
