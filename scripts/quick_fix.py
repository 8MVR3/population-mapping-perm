import numpy as np
import geopandas as gpd
import pandas as pd
import os

print("🚀 БЫСТРОЕ ИСПРАВЛЕНИЕ ДЛЯ ПРОДОЛЖЕНИЯ РАБОТЫ")

# 1. Проверяем что у нас есть
print("\n1. 📂 Проверяем файлы...")
files = []
for root, dirs, filenames in os.walk('data'):
    for f in filenames:
        if f.endswith('.geojson') or f.endswith('.csv'):
            files.append(os.path.join(root, f))

for f in files[:10]:  # покажем первые 10
    print(f"   - {f}")

# 2. Читаем точки населения (попробуем оба файла)
print("\n2. 📊 Загружаем точки населения...")
try:
    points = gpd.read_file("data/zones/perm_points.geojson")
    print(f"   ✅ Пермский край: {len(points)} точек")
except:
    try:
        points = gpd.read_file("data/zones/sverdlovsk_points.geojson")
        print(f"   ✅ Свердловская область: {len(points)} точек")
    except:
        print("   ❌ Не могу найти файлы с точками населения")

# 3. Создаем простой CSV для обучения на тестовых данных
print("\n3. 🎲 Создаем тестовые данные для обучения...")

# Генерируем синтетические данные для тестирования пайплайна
test_data = []
for i in range(100):
    test_data.append({
        'centroid_lon': 56.2 + np.random.uniform(-0.1, 0.1),
        'centroid_lat': 58.0 + np.random.uniform(-0.1, 0.1),
        'bld_area_m2': np.random.uniform(100, 1000),
        'bld_perimeter_m': np.random.uniform(40, 120),
        'area_perimeter_ratio': np.random.uniform(1.0, 3.0),
        'levels': np.random.randint(1, 9),
        'population': np.random.randint(10, 200)
    })

df = pd.DataFrame(test_data)
os.makedirs('data/train_real', exist_ok=True)
df.to_csv('data/train_real/test_training_data.csv', index=False)
print(f"   ✅ Создано 100 тестовых примеров")

print("\n🎯 Теперь можно обучать модель:")
print("python scripts/train_fixed_fixed.py --train-csv data/train_real/test_training_data.csv")
