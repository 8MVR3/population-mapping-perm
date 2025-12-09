import pandas as pd
import geopandas as gpd
from shapely import wkt

# Загружаем файл
df = pd.read_excel("data/Пермский край - Население.xlsx")
df['geometry'] = df['wkt_geom'].apply(wkt.loads)  # Преобразуем WKT в геометрию

# Создаем GeoDataFrame
gdf = gpd.GeoDataFrame(df, crs="EPSG:4326")

# Сохраняем в формат GeoJSON
gdf.to_file("data/zones/perm_zones.geojson", driver="GeoJSON")
