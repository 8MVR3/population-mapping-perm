import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import json
import os

print("🧪 ТЕСТИРОВАНИЕ ПАЙПЛАЙНА")

# 1. Проверим данные
print("\n1. 📊 Проверка данных...")
files = [
    'data/train_real/perm_real_features.csv',
    'data/train_real/realistic_train_data.csv',
    'data/train_real/test_training_data.csv'
]

for file in files:
    if os.path.exists(file):
        df = pd.read_csv(file)
        print(f"\n📁 {file}:")
        print(f"   Строк: {len(df)}, Колонок: {len(df.columns)}")
        print(f"   Колонки: {list(df.columns)}")
        if 'population' in df.columns:
            print(
                f"   Население: мин={df['population'].min():.1f}, макс={df['population'].max():.1f}, среднее={df['population'].mean():.1f}")

# 2. Создадим простую модель на realistic_train_data.csv
print("\n2. 🤖 Создание и тестирование модели...")
df = pd.read_csv('data/train_real/realistic_train_data.csv')
print(f"   Колонки в данных: {list(df.columns)}")

# Используем правильное название колонки
if 'area_to_perimeter_ratio' in df.columns:
    X = df[['centroid_lon', 'centroid_lat', 'bld_area_m2',
            'bld_perimeter_m', 'area_to_perimeter_ratio', 'levels']]
elif 'area_perimeter_ratio' in df.columns:
    X = df[['centroid_lon', 'centroid_lat', 'bld_area_m2',
            'bld_perimeter_m', 'area_perimeter_ratio', 'levels']]
else:
    print("   ❌ Не найдена колонка с соотношением площади/периметра")
    exit()

y = df['population']

model = RandomForestRegressor(n_estimators=50, random_state=42)
model.fit(X, y)

score = model.score(X, y)
print(f"   R² на тренировочных данных: {score:.3f}")

# 3. Сохраним модель
os.makedirs('models', exist_ok=True)
model_path = 'models/test_pipeline_model.pkl'
joblib.dump(model, model_path)

# 4. Сделаем предсказания
predictions = model.predict(X)
df_pred = df.copy()
df_pred['predicted_population'] = predictions

output_path = 'data/predictions/pipeline_test.csv'
os.makedirs('data/predictions', exist_ok=True)
df_pred.to_csv(output_path, index=False)

print(f"\n3. ✅ Пайплайн работает!")
print(f"   Модель сохранена: {model_path}")
print(f"   Предсказания сохранены: {output_path}")
print(f"   Среднее предсказание: {predictions.mean():.1f}")
print(f"   Общее предсказанное население: {predictions.sum():.0f}")

# 5. Протестируем на perm_real_features.csv
print("\n4. 📈 Тестирование на данных Пермского края...")
df_perm = pd.read_csv('data/train_real/perm_real_features.csv')
if 'area_to_perimeter_ratio' in df_perm.columns:
    X_perm = df_perm[['centroid_lon', 'centroid_lat', 'bld_area_m2',
                      'bld_perimeter_m', 'area_to_perimeter_ratio', 'levels']]
elif 'area_perimeter_ratio' in df_perm.columns:
    X_perm = df_perm[['centroid_lon', 'centroid_lat', 'bld_area_m2',
                      'bld_perimeter_m', 'area_perimeter_ratio', 'levels']]
else:
    print("   ❌ Нет колонки с соотношением в данных Перми")
    X_perm = None

if X_perm is not None:
    predictions_perm = model.predict(X_perm)
    print(f"   Предсказано население для {len(predictions_perm)} зданий")
    print(f"   Среднее предсказание: {predictions_perm.mean():.1f}")
    print(f"   Общее предсказанное население: {predictions_perm.sum():.0f}")

print("\n🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ!")
