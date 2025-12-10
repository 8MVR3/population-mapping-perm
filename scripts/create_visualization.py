import pandas as pd
import folium
from folium.plugins import HeatMap
import geopandas as gpd
import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        description='Создание визуализации населения на карте')
    parser.add_argument('--input', type=str, default='data/predictions/final_predictions.csv',
                        help='Входной CSV файл с предсказаниями')
    parser.add_argument(
        '--output', type=str, default='maps/population_map.html', help='Выходной HTML файл')
    parser.add_argument('--type', type=str, default='heatmap',
                        choices=['heatmap', 'points', 'both'], help='Тип визуализации')

    args = parser.parse_args()

    print("🗺️ Создание карты населения...")

    # Создаем папку для карт
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Загружаем данные
    try:
        df = pd.read_csv(args.input)
        print(f"✅ Загружено {len(df)} записей")
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        # Создаем тестовые данные
        print("📊 Создаем тестовые данные для визуализации...")
        df = pd.DataFrame({
            'lon': [56.2 + i*0.01 for i in range(100)],
            'lat': [58.0 + i*0.01 for i in range(100)],
            'predicted_population': [100 + i*10 for i in range(100)]
        })

    # Создаем карту
    center_lat = df['lat'].mean() if 'lat' in df.columns else 58.0
    center_lon = df['lon'].mean() if 'lon' in df.columns else 56.2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    if args.type in ['heatmap', 'both'] and 'lat' in df.columns and 'lon' in df.columns:
        print("🔥 Создание тепловой карты...")
        # Создаем данные для тепловой карты
        heat_data = []
        for idx, row in df.iterrows():
            if pd.notna(row['lat']) and pd.notna(row['lon']):
                weight = row['predicted_population'] if 'predicted_population' in df.columns else 1
                heat_data.append([row['lat'], row['lon'], weight])

        HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m)
        print(f"✅ Тепловая карта создана ({len(heat_data)} точек)")

    if args.type in ['points', 'both'] and 'lat' in df.columns and 'lon' in df.columns:
        print("📍 Добавление точек на карту...")
        for idx, row in df.head(100).iterrows():  # Ограничим 100 точками
            if pd.notna(row['lat']) and pd.notna(row['lon']):
                pop = row.get('predicted_population', 100)
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=5,
                    popup=f"Население: {pop:.0f} чел.",
                    color='blue',
                    fill=True
                ).add_to(m)

    # Добавляем слой OSM
    folium.TileLayer('openstreetmap').add_to(m)

    # Сохраняем карту
    m.save(args.output)
    print(f"💾 Карта сохранена: {args.output}")
    print(f"🌐 Откройте файл в браузере: file://{os.path.abspath(args.output)}")


if __name__ == "__main__":
    main()
