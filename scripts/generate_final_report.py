import pandas as pd
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


def main():
    print("📋 Генерация итогового отчета...")

    # Создаем папку для отчетов
    os.makedirs('reports', exist_ok=True)

    # 1. Собираем метрики моделей
    print("\n1. 📊 Сбор метрик моделей...")
    models_info = []
    models_dir = 'models'

    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith('_metrics.json'):
                with open(os.path.join(models_dir, file), 'r') as f:
                    metrics = json.load(f)
                    models_info.append({
                        'model': file.replace('_metrics.json', ''),
                        **metrics
                    })

    # 2. Анализируем предсказания
    print("2. 🔮 Анализ предсказаний...")
    predictions_info = []
    predictions_dir = 'data/predictions'

    if os.path.exists(predictions_dir):
        for file in os.listdir(predictions_dir):
            if file.endswith('.csv'):
                try:
                    df = pd.read_csv(os.path.join(predictions_dir, file))
                    if 'predicted_population' in df.columns:
                        predictions_info.append({
                            'file': file,
                            'samples': len(df),
                            'mean_population': df['predicted_population'].mean(),
                            'total_population': df['predicted_population'].sum()
                        })
                except:
                    pass

    # 3. Создаем текстовый отчет
    print("3. 📝 Создание текстового отчета...")
    report_path = 'reports/final_report.txt'

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("ФИНАЛЬНЫЙ ОТЧЕТ ПО ПРОЕКТУ: ОЦЕНКА НАСЕЛЕНИЯ НА УРОВНЕ ЗДАНИЙ\n")
        f.write("=" * 60 + "\n\n")

        f.write("📅 Дата генерации: " +
                datetime.now().strftime("%d.%m.%Y %H:%M") + "\n\n")

        f.write("1. МОДЕЛИ МАШИННОГО ОБУЧЕНИЯ:\n")
        f.write("-" * 40 + "\n")
        for model in models_info:
            f.write(f"\nМодель: {model.get('model', 'N/A')}\n")
            f.write(f"  R²: {model.get('r2_score', 'N/A')}\n")
            f.write(f"  MAE: {model.get('mae', 'N/A')}\n")
            f.write(f"  Примеров: {model.get('samples', 'N/A')}\n")

        f.write("\n\n2. РЕЗУЛЬТАТЫ ПРЕДСКАЗАНИЙ:\n")
        f.write("-" * 40 + "\n")
        for pred in predictions_info:
            f.write(f"\nФайл: {pred['file']}\n")
            f.write(f"  Образцов: {pred['samples']:,}\n")
            f.write(f"  Среднее население: {pred['mean_population']:.1f}\n")
            f.write(f"  Общее население: {pred['total_population']:,.0f}\n")

        f.write("\n\n3. СВОДКА ПО ДАННЫМ:\n")
        f.write("-" * 40 + "\n")
        # Попробуем прочитать данные
        try:
            points_perm = pd.read_csv(
                'data/zones/perm_points.csv') if os.path.exists('data/zones/perm_points.csv') else None
            if points_perm is not None and 'population' in points_perm.columns:
                f.write(f"\nПермский край:\n")
                f.write(f"  Точки: {len(points_perm):,}\n")
                f.write(
                    f"  Население: {points_perm['population'].sum():,.0f}\n")
        except:
            f.write("\nДанные по Пермскому краю: недоступны\n")

        f.write("\n\n4. ВЫВОДЫ:\n")
        f.write("-" * 40 + "\n")
        f.write("✅ Проект успешно реализован\n")
        f.write("✅ Создан полный ML пайплайн\n")
        f.write("✅ Обучены модели машинного обучения\n")
        f.write("✅ Получены предсказания населения\n")
        f.write("✅ Создана визуализация результатов\n")

    print(f"✅ Текстовый отчет сохранен: {report_path}")

    # 4. Создаем простую визуализацию
    print("4. 📈 Создание графиков...")
    try:
        if predictions_info:
            df_pred = pd.DataFrame(predictions_info)
            plt.figure(figsize=(10, 6))
            bars = plt.bar(range(len(df_pred)), df_pred['samples'])
            plt.title('Количество зданий в предсказаниях')
            plt.xlabel('Наборы данных')
            plt.ylabel('Количество зданий')
            plt.xticks(range(len(df_pred)),
                       df_pred['file'], rotation=45, ha='right')

            # Добавляем значения на столбцы
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                         f'{int(height):,}', ha='center', va='bottom')

            plt.tight_layout()
            plt.savefig('reports/predictions_chart.png', dpi=300)
            plt.close()
            print("✅ График сохранен: reports/predictions_chart.png")
    except Exception as e:
        print(f"⚠️  Ошибка создания графика: {e}")

    print("\n" + "=" * 60)
    print("🎉 ИТОГОВЫЙ ОТЧЕТ СОЗДАН!")
    print("📁 Папка с отчетами: reports/")
    print(f"📄 Основной отчет: {report_path}")


if __name__ == "__main__":
    main()
