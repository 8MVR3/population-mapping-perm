import pandas as pd
import os
import json


def analyze_xlsx_files():
    print("=" * 80)
    print("АНАЛИЗ РЕАЛЬНЫХ ДАННЫХ О НАСЕЛЕНИИ")
    print("=" * 80)

    # Список файлов для анализа
    files = [
        "data/Пермский край - Население.xlsx",
        "data/Свердловская область - Население.xlsx"
    ]

    results = {}

    for filepath in files:
        if not os.path.exists(filepath):
            print(f"\n❌ Файл не найден: {filepath}")
            continue

        print(f"\n{'='*60}")
        print(f"📋 АНАЛИЗ ФАЙЛА: {os.path.basename(filepath)}")
        print('='*60)

        try:
            # Читаем Excel файл
            df = pd.read_excel(filepath)

            print(
                f"📊 Размер данных: {df.shape[0]} строк × {df.shape[1]} столбцов")
            print(f"📁 Размер файла: {os.path.getsize(filepath) / 1024:.1f} KB")

            # Показываем все колонки
            print("\n📋 СТРУКТУРА ДАННЫХ:")
            for i, col in enumerate(df.columns):
                print(f"{i+1:2}. '{col}' ({df[col].dtype})")
                # Показываем примеры значений
                non_nan = df[col].dropna()
                if len(non_nan) > 0:
                    samples = non_nan.head(3).tolist()
                    print(f"    Примеры: {samples}")

            # Поиск колонок с населением
            print("\n👥 ПОИСК КОЛОНОК С НАСЕЛЕНИЕМ:")
            pop_columns = []
            for col in df.columns:
                col_lower = str(col).lower()
                if any(term in col_lower for term in ['насел', 'pop', 'inhab', 'жител', 'люд', 'people']):
                    pop_columns.append(col)
                    print(f"  ✅ '{col}': {df[col].sum():,.0f} человек")
                    print(
                        f"     Диапазон: {df[col].min():,.0f} - {df[col].max():,.0f}")

            # Поиск геометрии
            print("\n🗺️ ПОИСК ГЕОМЕТРИИ:")
            geo_columns = []
            for col in df.columns:
                col_lower = str(col).lower()
                if any(term in col_lower for term in ['wkt', 'geom', 'коорд', 'x', 'y', 'lat', 'lon', 'шир', 'долг']):
                    geo_columns.append(col)
                    print(f"  📍 '{col}'")

            # Сохраняем информацию
            results[os.path.basename(filepath)] = {
                'rows': df.shape[0],
                'columns': df.shape[1],
                'population_columns': pop_columns,
                'geometry_columns': geo_columns,
                'total_population': sum(df[col].sum() for col in pop_columns) if pop_columns else 0
            }

            # Сохраняем образец данных
            sample_file = f"data/{os.path.basename(filepath).replace('.xlsx', '')}_sample.csv"
            df.head(100).to_csv(sample_file, index=False, encoding='utf-8-sig')
            print(f"\n💾 Образец данных сохранен: {sample_file}")

        except Exception as e:
            print(f"❌ Ошибка при чтении файла: {e}")

    # Итоговый отчет
    print("\n" + "="*80)
    print("📈 ИТОГОВЫЙ ОТЧЕТ")
    print("="*80)
    for file, info in results.items():
        print(f"\n📄 {file}:")
        print(f"   📊 Размер: {info['rows']} строк, {info['columns']} колонок")
        print(f"   👥 Колонки с населением: {info['population_columns']}")
        print(f"   🗺️ Колонки с геометрией: {info['geometry_columns']}")
        print(f"   📈 Общее население: {info['total_population']:,.0f} чел.")


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    analyze_xlsx_files()
