import pandas as pd
import os

print("Создаем минимальные тестовые данные...")

# Создаем фичи
features = pd.DataFrame({
    'building_id': [1, 2, 3, 4, 5],
    'centroid_lon': [56.23, 56.231, 56.232, 56.233, 56.234],
    'centroid_lat': [58.01, 58.011, 58.012, 58.013, 58.014],
    'bld_area_m2': [100, 150, 200, 120, 180],
    'bld_perimeter_m': [40, 50, 60, 45, 55],
    'area_to_perimeter_ratio': [2.5, 3.0, 3.33, 2.67, 3.27],
    'levels': [1, 2, 3, 2, 1],
    'population': [10, 20, 30, 15, 25]
})

# Сохраняем
os.makedirs('data/test_minimal', exist_ok=True)
features.to_csv('data/test_minimal/features.csv', index=False)

print(f"✅ Создано {len(features)} тестовых записей")
print("Запустите обучение:")
print("python scripts/train_fixed.py --features-csv data/test_minimal/features.csv --train-csv data/test_minimal/features.csv")
