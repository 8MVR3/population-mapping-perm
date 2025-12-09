import os
import subprocess
import sys

print("="*60)
print("🚀 ПОЛНЫЙ ПАЙПЛАЙН ОЦЕНКИ НАСЕЛЕНИЯ")
print("="*60)


def run_step(name, command):
    print(f"\n{'='*40}")
    print(f"ШАГ: {name}")
    print('='*40)
    print(f"Выполняем: {command}")

    try:
        result = subprocess.run(command, shell=True, check=True,
                                capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        if result.stderr:
            print("⚠️ Предупреждения:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка в шаге '{name}':")
        print(e.stderr)
        return False


# Шаги пайплайна
steps = [
    ("Анализ реальных данных", "python scripts/check_real_data.py"),
    ("Создание тренировочных данных", "python scripts/create_realistic_test_data.py"),
    ("Обучение модели", "python scripts/train_fixed_fixed.py --features-csv data/train_real/realistic_train_data.csv --train-csv data/train_real/realistic_train_data.csv --model-save-path models/population_model_realistic.pkl"),
    ("Предсказание населения", "python scripts/predict_fixed_real.py --features-csv data/train_real/realistic_train_data.csv --output-csv data/predictions/realistic_predictions.csv"),
    ("Создание отчета", "python scripts/create_report.py")
]

# Создаем необходимые директории
os.makedirs("data/predictions", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Выполняем все шаги
success = True
for step_name, command in steps:
    if not run_step(step_name, command):
        success = False
        print(f"\n⚠️ Пайплайн остановлен на шаге: {step_name}")
        break

print("\n" + "="*60)
if success:
    print("✅ ПАЙПЛАЙН УСПЕШНО ЗАВЕРШЕН!")
    print("\n📊 РЕЗУЛЬТАТЫ:")
    print("   - Модель: models/population_model_realistic.pkl")
    print("   - Предсказания: data/predictions/realistic_predictions.csv")
    print("   - Отчет: см. выше")
else:
    print("❌ ПАЙПЛАЙН ЗАВЕРШИЛСЯ С ОШИБКАМИ")
print("="*60)
