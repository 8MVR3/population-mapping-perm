import pandas as pd
import joblib
import os
import click


@click.command()
@click.option('--model-path', default='models/population_model.pkl', help='Путь к обученной модели')
@click.option('--features-csv', required=True, help='CSV файл с фичами для предсказания')
@click.option('--output-csv', required=True, help='Выходной CSV с предсказаниями')
def main(model_path, features_csv, output_csv):
    print("="*60)
    print("ПРЕДСКАЗАНИЕ НАСЕЛЕНИЯ ДЛЯ ЗДАНИЙ")
    print("="*60)

    # 1. Загрузка модели
    print("\n1. Загрузка модели...")
    if not os.path.exists(model_path):
        print(f"❌ Модель не найдена: {model_path}")
        return

    model = joblib.load(model_path)
    print(f"✅ Модель загружена: {model_path}")

    # 2. Загрузка данных для предсказания
    print("\n2. Загрузка данных для предсказания...")
    if not os.path.exists(features_csv):
        print(f"❌ Файл не найден: {features_csv}")
        return

    df = pd.read_csv(features_csv)
    print(f"✅ Загружено {len(df)} зданий")

    # 3. Подготовка данных
    print("\n3. Подготовка данных...")
    # Убедимся, что есть все нужные колонки
    required_cols = ['centroid_lon', 'centroid_lat', 'bld_area_m2',
                     'bld_perimeter_m', 'area_to_perimeter_ratio', 'levels']

    # Если есть building_id, сохраним его
    if 'building_id' in df.columns:
        building_ids = df['building_id']
    else:
        building_ids = pd.Series(range(1, len(df) + 1))

    # Проверяем наличие колонок
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"❌ Отсутствуют колонки: {missing_cols}")
        return

    X = df[required_cols]
    print(f"   Используется {X.shape[1]} признаков")

    # 4. Предсказание
    print("\n4. Предсказание населения...")
    predictions = model.predict(X)
    df_pred = pd.DataFrame({
        'building_id': building_ids,
        'predicted_population': predictions
    })

    # Добавляем оригинальные фичи, если нужно
    for col in required_cols:
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

    print("\n" + "="*60)
    print("🎉 ПРЕДСКАЗАНИЕ ЗАВЕРШЕНО!")
    print("="*60)


if __name__ == '__main__':
    main()
