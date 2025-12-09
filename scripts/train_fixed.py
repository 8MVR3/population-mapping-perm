#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
train_fixed.py
Исправленная тренировка модели на фичах и населении.
"""

import logging
from pathlib import Path
import click
import pandas as pd
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--features-csv", default="data/features/building_features.csv")
@click.option("--train-csv", default="data/train/train_buildings_population.csv")
@click.option("--model-out", default="models/rf_pop_model.joblib")
@click.option("--test-size", default=0.2)
def main(features_csv, train_csv, model_out, test_size):
    print("=" * 60)
    print("ТРЕНИРОВКА МОДЕЛИ РАСПРЕДЕЛЕНИЯ НАСЕЛЕНИЯ")
    print("=" * 60)

    # Проверяем существование файлов
    feat_path = Path(features_csv)
    train_path = Path(train_csv)

    if not feat_path.exists():
        print(f"❌ Файл с фичами не найден: {features_csv}")
        return

    if not train_path.exists():
        print(f"❌ Файл с тренировочными данными не найден: {train_csv}")
        return

    # 1. Загружаем данные
    print("\n1. Загрузка данных...")
    feats = pd.read_csv(features_csv)
    train = pd.read_csv(train_csv)

    print(f"   Фичи: {feats.shape[0]} строк, {feats.shape[1]} колонок")
    print(f"   Целевая переменная: {train.shape[0]} строк")

    # 2. Объединяем данные
    # Проверяем, что количество строк совпадает
    if len(feats) != len(train):
        print(
            f"⚠️  Внимание: разное количество строк ({len(feats)} vs {len(train)})")
        print("   Обрезаем по минимальному количеству...")
        min_len = min(len(feats), len(train))
        feats = feats.iloc[:min_len]
        train = train.iloc[:min_len]

    # Объединяем фичи и target
    df = pd.concat([feats.reset_index(drop=True),
                   train[["population"]].reset_index(drop=True)], axis=1)

    # Убираем строки где population NaN
    initial_rows = len(df)
    df = df.dropna(subset=["population"])
    print(
        f"   После удаления NaN в population: {len(df)} строк (удалено {initial_rows - len(df)})")

    # 3. Подготовка данных
    print("\n2. Подготовка данных...")
    X = df.drop(columns=["population"])
    y = df["population"]

    # Оставляем только числовые колонки
    X_numeric = X.select_dtypes(include=[np.number])

    # Заполняем пропущенные значения
    X_filled = X_numeric.fillna(0)

    print(f"   Признаков (X): {X_filled.shape[1]}")
    print(f"   Целевая переменная (y): {y.shape[0]} значений")
    print(f"   Среднее население: {float(y.mean().iloc[0]):.2f}")
    print(f"   Максимальное население: {y.max():.2f}")

    # 4. Разделение на train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X_filled, y, test_size=test_size, random_state=42, shuffle=True
    )

    print(f"\n3. Разделение данных (test_size={test_size}):")
    print(f"   Train: {X_train.shape[0]} образцов")
    print(f"   Test:  {X_test.shape[0]} образцов")

    # 5. Тренировка модели
    print("\n4. Тренировка RandomForest...")
    rf = RandomForestRegressor(
        n_estimators=100,  # Уменьшил для скорости теста
        max_depth=10,
        min_samples_split=5,
        n_jobs=-1,
        random_state=42
    )

    rf.fit(X_train, y_train)
    print("   ✅ Модель обучена!")

    # 6. Оценка модели
    print("\n5. Оценка модели:")
    y_pred_train = rf.predict(X_train)
    y_pred_test = rf.predict(X_test)

    # Метрики - ИСПРАВЛЕННЫЕ ВЫЗОВЫ (без squared)
    train_mae = mean_absolute_error(y_train, y_pred_train)
    train_rmse = np.sqrt(mean_squared_error(
        y_train, y_pred_train))  # Вместо squared=False
    train_r2 = r2_score(y_train, y_pred_train)

    test_mae = mean_absolute_error(y_test, y_pred_test)
    test_rmse = np.sqrt(mean_squared_error(
        y_test, y_pred_test))  # Вместо squared=False
    test_r2 = r2_score(y_test, y_pred_test)

    print("   Тренировочные данные:")
    print(f"     MAE:  {train_mae:.4f}")
    print(f"     RMSE: {train_rmse:.4f}")
    print(f"     R²:   {train_r2:.4f}")

    print("   Тестовые данные:")
    print(f"     MAE:  {test_mae:.4f}")
    print(f"     RMSE: {test_rmse:.4f}")
    print(f"     R²:   {test_r2:.4f}")

    # 7. Важность признаков
    print("\n6. Важность признаков (топ-10):")
    feature_importance = pd.DataFrame({
        "feature": X_filled.columns,
        "importance": rf.feature_importances_
    }).sort_values("importance", ascending=False)

    for i, (_, row) in enumerate(feature_importance.head(10).iterrows()):
        print(f"     {i+1:2d}. {row['feature']:20s} {row['importance']:.4f}")

    # 8. Сохранение модели
    print("\n7. Сохранение модели...")
    model_path = Path(model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    # Сохраняем модель и информацию о признаках
    model_data = {
        "model": rf,
        "features": X_filled.columns.tolist(),
        "feature_importance": feature_importance.to_dict("records"),
        "metrics": {
            "test_mae": test_mae,
            "test_rmse": test_rmse,
            "test_r2": test_r2
        }
    }

    joblib.dump(model_data, model_path)
    print(f"   ✅ Модель сохранена: {model_path}")

    # 9. Предсказание на нескольких примерах
    print("\n8. Примеры предсказаний:")
    sample_indices = np.random.choice(
        len(X_test), min(5, len(X_test)), replace=False)
    for i, idx in enumerate(sample_indices):
        actual = y_test.iloc[idx]
        predicted = y_pred_test[idx]
        error = abs(actual - predicted)
        print(
            f"   Пример {i+1}: Факт={actual:.2f}, Предсказано={predicted:.2f}, Ошибка={error:.2f}")

    print("\n" + "=" * 60)
    print("✅ ТРЕНИРОВКА ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 60)


if __name__ == "__main__":
    main()
