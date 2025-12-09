#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
predict_fixed.py
Предсказание населения по зданиям.
"""

import logging
from pathlib import Path
import click
import geopandas as gpd
import pandas as pd
import joblib
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--bld-features-geojson", default="data/features/building_features.geojson")
@click.option("--model-joblib", default="models/rf_pop_model.joblib")
@click.option("--out-geojson", default="data/predictions/buildings_with_pred_pop.geojson")
def main(bld_features_geojson, model_joblib, out_geojson):
    print("=" * 60)
    print("ПРЕДСКАЗАНИЕ НАСЕЛЕНИЯ ПО ЗДАНИЯМ")
    print("=" * 60)

    # 1. Проверяем файлы
    if not Path(bld_features_geojson).exists():
        print(f"❌ Файл с фичами не найден: {bld_features_geojson}")
        return

    if not Path(model_joblib).exists():
        print(f"❌ Модель не найдена: {model_joblib}")
        print("   Сначала обучите модель: python train_fixed.py")
        return

    # 2. Загружаем данные
    print("\n1. Загрузка данных...")
    bld = gpd.read_file(bld_features_geojson)
    print(f"   Зданий: {len(bld)}")
    print(f"   Колонок: {len(bld.columns)}")

    # 3. Загружаем модель
    print("\n2. Загрузка модели...")
    try:
        model_data = joblib.load(model_joblib)
        model = model_data["model"]
        feat_cols = model_data["features"]
        print(f"   ✅ Модель загружена")
        print(f"   Признаков в модели: {len(feat_cols)}")

        # Показываем важность признаков если есть
        if "feature_importance" in model_data:
            print(f"   Топ-3 важных признака:")
            for i, feat in enumerate(model_data["feature_importance"][:3]):
                print(
                    f"     {i+1}. {feat['feature']}: {feat['importance']:.4f}")
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")
        return

    # 4. Подготавливаем признаки для предсказания
    print("\n3. Подготовка признаков...")

    # Проверяем, что все нужные признаки есть в данных
    missing_features = [f for f in feat_cols if f not in bld.columns]
    if missing_features:
        print(f"⚠️  Отсутствуют признаки: {missing_features[:5]}...")
        print("   Заполняем нулями...")
        for feat in missing_features:
            bld[feat] = 0

    # Выбираем признаки
    X = bld[feat_cols].copy()

    # Заполняем пропущенные значения
    X_filled = X.fillna(0)

    # Проверяем типы данных
    X_numeric = X_filled.select_dtypes(include=[np.number])
    non_numeric = [
        col for col in X_filled.columns if col not in X_numeric.columns]

    if non_numeric:
        print(f"⚠️  НЕчисловые признаки будут проигнорированы: {non_numeric}")
        X_filled = X_numeric

    print(f"   Признаков для предсказания: {X_filled.shape[1]}")
    print(f"   Строк для предсказания: {X_filled.shape[0]}")

    # 5. Предсказание
    print("\n4. Выполнение предсказаний...")
    try:
        preds = model.predict(X_filled)
        print(f"   ✅ Предсказания выполнены: {len(preds)} значений")
    except Exception as e:
        print(f"❌ Ошибка предсказания: {e}")
        return

    # 6. Сохраняем результаты
    print("\n5. Сохранение результатов...")

    # Добавляем предсказания к данным
    bld["pred_population"] = preds

    # Создаем папку если нет
    outp = Path(out_geojson)
    outp.parent.mkdir(parents=True, exist_ok=True)

    # Сохраняем GeoJSON
    bld.to_file(out_geojson, driver="GeoJSON")

    # Также сохраняем CSV для анализа
    csv_path = out_geojson.replace(".geojson", ".csv")
    result_df = pd.DataFrame({
        "building_id": bld.index,
        "predicted_population": preds
    })
    if "id" in bld.columns:
        result_df["building_id"] = bld["id"]

    result_df.to_csv(csv_path, index=False)

    # 7. Статистика результатов
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ПРЕДСКАЗАНИЯ:")
    print(f"✅ Файлы сохранены:")
    print(f"   GeoJSON: {out_geojson}")
    print(f"   CSV:     {csv_path}")

    print(f"\n📊 Статистика предсказаний:")
    print(f"   Всего зданий: {len(preds)}")
    print(f"   Общее население (предсказанное): {preds.sum():.0f} чел.")
    print(f"   Среднее на здание: {preds.mean():.2f} чел.")
    print(f"   Максимальное: {preds.max():.2f} чел.")
    print(f"   Минимальное: {preds.min():.2f} чел.")

    # Распределение по категориям
    print(f"\n📈 Распределение предсказаний:")
    if "building" in bld.columns:
        for bld_type in bld["building"].unique()[:5]:  # первые 5 типов
            mask = bld["building"] == bld_type
            if mask.any():
                avg_pop = preds[mask].mean()
                count = mask.sum()
                print(
                    f"   {bld_type}: {count} зданий, среднее {avg_pop:.1f} чел.")

    print(f"\n🔍 Примеры предсказаний (первые 5):")
    for i in range(min(5, len(preds))):
        bld_type = bld.iloc[i]["building"] if "building" in bld.columns else "unknown"
        print(f"   Здание {i+1}: тип={bld_type}, население={preds[i]:.2f}")

    print("\n" + "=" * 60)
    print("✅ ПРЕДСКАЗАНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)


if __name__ == "__main__":
    main()
