import osmnx as ox
import geopandas as gpd
import argparse
import os

# Установите VPN и измените Overpass URL если нужно
# ox.settings.overpass_url = "https://overpass-api.de/api/interpreter"


def main():
    parser = argparse.ArgumentParser(description='Быстрая загрузка OSM зданий')
    parser.add_argument('--city', type=str, default='Пермь',
                        help='Название города')
    parser.add_argument(
        '--output', type=str, default='data/osm_real/buildings.geojson', help='Выходной файл')
    parser.add_argument('--radius', type=float, default=5000,
                        help='Радиус в метрах от центра')

    args = parser.parse_args()

    print(f"🔍 Загружаем OSM данные для {args.city}...")

    try:
        # Получаем координаты города
        city = ox.geocode_to_gdf(args.city)
        center_point = city.geometry.centroid.iloc[0]

        # Загружаем здания в радиусе
        buildings = ox.geometries.geometries_from_point(
            (center_point.y, center_point.x),
            tags={'building': True},
            dist=args.radius
        )

        # Фильтруем только здания
        buildings = buildings[buildings['building'].notna()]

        print(f"✅ Загружено {len(buildings)} зданий")

        # Сохраняем
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        buildings.to_file(args.output, driver='GeoJSON')
        print(f"💾 Сохранено в {args.output}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n🔧 Возможные решения:")
        print("1. Проверьте VPN подключение")
        print("2. Попробуйте другой сервер:")
        print("   ox.settings.overpass_url = 'https://overpass-api.de/api/interpreter'")


if __name__ == "__main__":
    main()
