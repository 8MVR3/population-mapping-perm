import pandas as pd
import joblib
import os
import click


@click.command()
@click.option('--model-path', default='models/population_model_realistic.pkl', help='Путь к обученной модели')
@click.option('--features-csv', required=True, help='CSV файл с фичами для предсказания')
@click.option('--output-csv', required=True, help='Выходной CSV с предсказаниями')
def main(model_path, features_csv, output_csv):
    print("="*60)
    print("ПРЕДСКАЗАНИЕ НАСЕЛЕНИЯ ДЛЯ ЗДАНИЙ (ИСПРАВЛЕННАЯ ВЕРСИЯ)")
    print("="*60)

    # 1. Загрузка модели
    print("\n1. Загрузка модели...")
    if not os.path.exists(model_path):
        print(f"❌ Модель не найдена: {model_path}")
        return

    model = joblib.load(model_path)
    print(f"✅ Модель загружена: {model_path}")

    # Проверяем признаки модели
    try:
        model_features = list(model.feature_names_in_)
        print(f"   Модель ожидает признаки: {model_features}")
    except:
        print("   ⚠️ Модель не содержит информации о признаках")
        model_features = ['centroid_lon', 'centroid_lat', 'bld_area_m2',
                          'bld_perimeter_m', 'area_to_perimeter_ratio', 'levels']

    # 2. Загрузка данных для предсказания
    print("\n2. Загрузка данных для предсказания...")
    if not os.path.exists(features_csv):
        print(f"❌ Файл не найден: {features_csv}")
        return

    df = pd.read_csv(features_csv)
    print(f"✅ Загружено {len(df)} зданий")
    print(f"   Колонки в данных: {list(df.columns)}")

    # 3. Подготовка данных
    print("\n3. Подготовка данных...")

    # Если есть building_id, сохраним его
    if 'building_id' in df.columns:
        building_ids = df['building_id']
    else:
        building_ids = pd.Series(range(1, len(df) + 1), name='building_id')

    # Проверяем наличие нужных колонок
    missing_cols = [col for col in model_features if col not in df.columns]
    if missing_cols:
        print(f"❌ Отсутствуют колонки: {missing_cols}")
        print(f"   Доступные колонки: {list(df.columns)}")
        return

    X = df[model_features]
    print(f"   Используется {X.shape[1]} признаков: {list(X.columns)}")

    # 4. Предсказание
    print("\n4. Предсказание населения...")
    predictions = model.predict(X)
    df_pred = pd.DataFrame({
        'building_id': building_ids,
        'predicted_population': predictions
    })

    # Добавляем оригинальные фичи
    for col in model_features:
        df_pred[col] = df[col].values

    # 5. Сохранение результатов
    print("\n5. Сохранение результатов...")
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_pred.to_csv(output_csv, index=False)
    print(f"✅ Предсказания сохранены: {output_csv}")

    # 6. Статистика
    print("\n6. Статистика предсказаний:")
    print(f"   Всего зданий: {len(df_pred)}")
    print(
        f"   Среднее население: {df_pred['predicted_population'].mean():.2f}")
    print(f"   Общее население: {df_pred['predicted_population'].sum():.0f}")
    print(f"   Минимум: {df_pred['predicted_population'].min():.2f}")
    print(f"   Максимум: {df_pred['predicted_population'].max():.2f}")

    # Показываем первые 5 предсказаний
    print("\n7. Примеры предсказаний (первые 5):")
    for i in range(min(5, len(df_pred))):
        row = df_pred.iloc[i]
        print(
            f"   Здание {row['building_id']}: {row['predicted_population']:.1f} чел.")

    print("\n" + "="*60)
    print("🎉 ПРЕДСКАЗАНИЕ ЗАВЕРШЕНО!")
    print("="*60)


if __name__ == '__main__':
    main()
