import subprocess
import sys
import os


def run_command(cmd):
    """Запускает команду и возвращает результат"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"✅ Успешно: {cmd}")
            return True
        else:
            print(f"❌ Ошибка в {cmd}:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"⚠️  Исключение при выполнении {cmd}: {e}")
        return False


def main():
    print("🚀 УПРОЩЕННЫЙ ПАЙПЛАЙН ОЦЕНКИ НАСЕЛЕНИЯ")
    print("=" * 60)

    steps = [
        ("Анализ данных", "python scripts/analyze_real_data.py"),
        ("Создание фичей", "python scripts/featurize_simple.py"),
        ("Обучение модели", "python scripts/train_fixed_fixed.py --features-csv data/train_real/realistic_train_data.csv --train-csv data/train_real/realistic_train_data.csv --model-save-path models/simple_model.pkl"),
        ("Предсказание", "python scripts/predict_fixed_real.py --model-path models/simple_model.pkl --features-csv data/train_real/realistic_train_data.csv --output-csv data/predictions/simple_predictions.csv"),
        ("Визуализация", "python scripts/create_visualization.py --input data/predictions/simple_predictions.csv --output maps/simple_map.html"),
        ("Отчет", "python scripts/create_final_report.py")
    ]

    for step_name, command in steps:
        print(f"\n{'='*40}")
        print(f"ШАГ: {step_name}")
        print(f"Команда: {command}")
        input("Нажмите Enter для продолжения...")

        if not run_command(command):
            print(f"⚠️  Пропускаем шаг: {step_name}")
            continue

    print("\n" + "=" * 60)
    print("🎉 ПАЙПЛАЙН ЗАВЕРШЕН!")
    print("📊 Результаты в папках:")
    print("   - models/ - обученные модели")
    print("   - data/predictions/ - предсказания")
    print("   - maps/ - визуализации")
    print("   - reports/ - отчеты")


if __name__ == "__main__":
    main()
