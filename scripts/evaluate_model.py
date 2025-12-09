import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os

print("="*60)
print("ОЦЕНКА МОДЕЛИ НА ТЕСТОВЫХ ДАННЫХ")
print("="*60)

# Загружаем предсказания и истинные значения
preds_path = "data/predictions/predictions.csv"
true_path = "data/train_real/realistic_train_data.csv"

if not os.path.exists(preds_path):
    print(f"❌ Файл с предсказаниями не найден: {preds_path}")
    exit()

if not os.path.exists(true_path):
    print(f"❌ Файл с истинными значениями не найден: {true_path}")
    exit()

print("\n📥 Загрузка данных...")
preds = pd.read_csv(preds_path)
true_data = pd.read_csv(true_path)

print(f"   Предсказания: {len(preds)} зданий")
print(f"   Истинные данные: {len(true_data)} зданий")

# Объединяем данные
if 'building_id' in preds.columns and 'building_id' in true_data.columns:
    combined = pd.merge(
        preds, true_data[['building_id', 'population']], on='building_id', how='inner')
else:
    # Если нет building_id, используем индексы
    combined = preds.copy()
    combined['true_population'] = true_data['population'].values[:len(preds)]

print(f"\n📊 После объединения: {len(combined)} зданий")

# Вычисляем метрики
mae = mean_absolute_error(
    combined['true_population'], combined['predicted_population'])
rmse = np.sqrt(mean_squared_error(
    combined['true_population'], combined['predicted_population']))
r2 = r2_score(combined['true_population'], combined['predicted_population'])

print(f"\n📈 МЕТРИКИ МОДЕЛИ:")
print(f"   MAE: {mae:.4f} (средняя абсолютная ошибка)")
print(f"   RMSE: {rmse:.4f} (среднеквадратичная ошибка)")
print(f"   R²: {r2:.4f} (коэффициент детерминации)")

# Показываем примеры
print(f"\n📋 ПРИМЕРЫ (первые 5 зданий):")
for i in range(min(5, len(combined))):
    row = combined.iloc[i]
    print(f"   Здание {row['building_id']}: предсказано={row['predicted_population']:.1f}, истинное={row['true_population']:.1f}, ошибка={abs(row['predicted_population'] - row['true_population']):.1f}")
