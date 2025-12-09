import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import click


@click.command()
@click.option('--features-csv', required=True, help='CSV файл с фичами зданий')
@click.option('--train-csv', required=True, help='CSV файл с тренировочными данными')
@click.option('--model-save-path', default='models/population_model.pkl', help='Путь для сохранения модели')
def main(features_csv, train_csv, model_save_path):
    print("="*60)
    print("ТРЕНИРОВКА МОДЕЛИ РАСПРЕДЕЛЕНИЯ НАСЕЛЕНИЯ")
    print("="*60)

    # 1. Загрузка данных
    print("\n1. Загрузка данных...")

    if not os.path.exists(features_csv):
        print(f"❌ Файл с фичами не найден: {features_csv}")
        return

    if not os.path.exists(train_csv):
        print(f"❌ Файл с тренировочными данными не найден: {train_csv}")
        return

    df_features = pd.read_csv(features_csv)
    df_train = pd.read_csv(train_csv)

    print(
        f"   Фичи: {df_features.shape[0]} строк, {df_features.shape[1]} колонок")
    print(
        f"   Тренировочные данные: {df_train.shape[0]} строк, {df_train.shape[1]} колонок")

    # 2. Подготовка данных
    print("\n2. Подготовка данных...")

    # Если файлы одинаковые, используем один DataFrame
    if features_csv == train_csv:
        df = df_features
    else:
        # Объединяем по building_id
        if 'building_id' in df_features.columns and 'building_id' in df_train.columns:
            df = pd.merge(df_features, df_train[[
                          'building_id', 'population']], on='building_id', how='inner')
        else:
            # Если нет building_id, используем индексы
            df = df_features.copy()
            df['population'] = df_train['population'].values[:len(df)]

    # Удаляем строки без населения
    initial_count = len(df)
    df = df.dropna(subset=['population'])
    removed_count = initial_count - len(df)

    print(
        f"   После удаления NaN в population: {len(df)} строк (удалено {removed_count})")

    if len(df) == 0:
        print("❌ Нет данных для обучения!")
        return

    # Определяем фичи и целевую переменную
    exclude_cols = ['building_id', 'population']
    feature_cols = [col for col in df.columns if col not in exclude_cols]

    X = df[feature_cols]
    y = df['population']

    print(f"   Признаков (X): {X.shape[1]}")
    print(f"   Целевая переменная (y): {y.shape[0]} значений")

    # Исправленная строка - преобразуем y.mean() в float
    try:
        y_mean = float(y.mean())
        print(f"   Среднее население: {y_mean:.2f}")
    except Exception as e:
        print(f"   Среднее население: {y.mean():.2f}")

    # 3. Разделение данных
    print("\n3. Разделение данных...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"   Обучающая выборка: {X_train.shape[0]} образцов")
    print(f"   Тестовая выборка: {X_test.shape[0]} образцов")

    # 4. Обучение модели
    print("\n4. Обучение модели RandomForest...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)
    print("   ✅ Модель обучена")

    # 5. Оценка модели
    print("\n5. Оценка модели...")
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print(f"   MAE: {mae:.4f}")
    print(f"   RMSE: {rmse:.4f}")
    print(f"   R²: {r2:.4f}")

    # 6. Важность признаков
    print("\n6. Важность признаков (топ-10):")
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    for i, row in feature_importance.head(10).iterrows():
        print(f"   {row['feature']}: {row['importance']:.4f}")

    # 7. Сохранение модели
    print("\n7. Сохранение модели...")
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump(model, model_save_path)
    print(f"   ✅ Модель сохранена: {model_save_path}")

    # 8. Сохранение метрик
    metrics = {
        'mae': float(mae),
        'rmse': float(rmse),
        'r2': float(r2),
        'n_samples': int(len(df)),
        'n_features': int(len(feature_cols))
    }

    metrics_path = model_save_path.replace('.pkl', '_metrics.json')
    import json
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"   ✅ Метрики сохранены: {metrics_path}")

    print("\n" + "="*60)
    print("🎉 ТРЕНИРОВКА ЗАВЕРШЕНА УСПЕШНО!")
    print("="*60)


if __name__ == '__main__':
    main()
