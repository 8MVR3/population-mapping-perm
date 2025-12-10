import osmnx as ox
import geopandas as gpd
import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        description='Загрузка OSM полигонов зданий')
    parser.add_argument('--north', type=float, required=True)
    parser.add_argument('--south', type=float, required=True)
    parser.add_argument('--east', type=float, required=True)
    parser.add_argument('--west', type=float, required=True)
    parser.add_argument('--out-dir', type=str, default='data/osm_real')

    args = parser.parse_args()

    print(
        f"🔍 Загружаем OSM полигоны зданий для bbox: {args.north}, {args.south}, {args.east}, {args.west}")

    # Загружаем только полигоны и мультиполигоны зданий
    tags = {'building': True}
    try:
        gdf = ox.geometries_from_bbox(
            args.north, args.south, args.east, args.west,
            tags=tags
        )

        # Фильтруем только полигоны (убираем точки)
        gdf = gdf[gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])]

        print(f"✅ Загружено {len(gdf)} полигонов зданий")

        # Сохраняем
        os.makedirs(args.out_dir, exist_ok=True)
        output_path = os.path.join(args.out_dir, 'buildings_polygons.geojson')
        gdf.to_file(output_path, driver='GeoJSON')
        print(f"💾 Сохранено в {output_path}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()
