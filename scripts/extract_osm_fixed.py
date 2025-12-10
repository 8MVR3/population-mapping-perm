import osmnx as ox
import geopandas as gpd
import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        description='Загрузка OSM полигонов зданий (исправленный)')
    parser.add_argument('--north', type=float, required=True)
    parser.add_argument('--south', type=float, required=True)
    parser.add_argument('--east', type=float, required=True)
    parser.add_argument('--west', type=float, required=True)
    parser.add_argument('--out-dir', type=str, default='data/osm_real')

    args = parser.parse_args()

    print(
        f"🔍 Загружаем OSM данные для bbox: {args.north}, {args.south}, {args.east}, {args.west}")

    try:
        # Загружаем здания как footprints (полигоны)
        buildings = ox.features.features_from_bbox(
            north=args.north,
            south=args.south,
            east=args.east,
            west=args.west,
            tags={'building': True}
        )

        # Фильтруем только полигоны
        buildings = buildings[buildings.geometry.type.isin(
            ['Polygon', 'MultiPolygon'])]

        print(f"✅ Загружено {len(buildings)} полигонов зданий")

        # Сохраняем
        os.makedirs(args.out_dir, exist_ok=True)
        output_path = os.path.join(
            args.out_dir, 'buildings_polygons_fixed.geojson')
        buildings.to_file(output_path, driver='GeoJSON')
        print(f"💾 Сохранено в {output_path}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n🔧 Используем альтернативный метод...")
        # Альтернативный подход
        try:
            import geopandas as gpd
            from shapely.geometry import box
            import requests

            # Создаем bbox
            bbox = f"{args.west},{args.south},{args.east},{args.north}"
            overpass_url = "https://overpass-api.de/api/interpreter"
            query = f"""
            [out:json][timeout:25];
            (
              way["building"]({bbox});
              relation["building"]({bbox});
            );
            out body;
            >;
            out skel qt;
            """

            response = requests.get(overpass_url, params={'data': query})
            data = response.json()

            # Обработка данных (упрощенно)
            print(f"Получено {len(data['elements'])} элементов")

        except Exception as e2:
            print(f"❌ Ошибка в альтернативном методе: {e2}")


if __name__ == "__main__":
    main()
