#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_osm.py
Скрипт для скачивания OSM-данных (здания, дороги, POI) для bounding box или имени города.
Совместим с OSMnx 2.x
"""

import logging
from pathlib import Path
import click
import osmnx as ox
import geopandas as gpd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ox.settings.use_cache = True
ox.settings.log_console = False


@click.command()
@click.option("--place", default=None, help="Place name for osmnx (e.g. 'Perm, Russia') OR leave empty and use bbox.")
@click.option("--north", type=float, default=None)
@click.option("--south", type=float, default=None)
@click.option("--east", type=float, default=None)
@click.option("--west", type=float, default=None)
@click.option("--out-dir", default="data/osm", help="Output directory")
def main(place, north, south, east, west, out_dir):

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # ---------- LOAD DATA ----------
    if place:
        logger.info(f"Downloading data for place: {place}")

        # Buildings
        gdf_buildings = ox.features_from_place(
            place, tags={"building": True}
        )

        # Roads graph
        gdf_roads = ox.graph_from_place(
            place, network_type="drive"
        )

        # POI
        gdf_pois = ox.features_from_place(
            place, tags={"amenity": True, "shop": True, "leisure": True}
        )

    else:
        assert None not in (north, south, east, west), "Provide bbox or place"

        bbox = (north, south, east, west)
        logger.info(f"Downloading data for bbox: {bbox}")

        gdf_buildings = ox.features_from_bbox(
            bbox, tags={"building": True}
        )

        gdf_roads = ox.graph_from_bbox(
            bbox, network_type="drive"
        )

        gdf_pois = ox.features_from_bbox(
            bbox, tags={"amenity": True, "shop": True, "leisure": True}
        )

    # ---------- NORMALIZE ----------
    if not isinstance(gdf_buildings, gpd.GeoDataFrame):
        gdf_buildings = gpd.GeoDataFrame(gdf_buildings)

    buildings = gdf_buildings.copy()

    # Convert graph → edges GeoDataFrame
    edges = ox.graph_to_gdfs(
        gdf_roads,
        nodes=False,
        edges=True,
        node_geometry=False,
        fill_edge_geometry=True
    )[0]

    if not isinstance(gdf_pois, gpd.GeoDataFrame):
        gdf_pois = gpd.GeoDataFrame(gdf_pois)

    pois = gdf_pois.copy()

    # ---------- SAVE ----------
    bld_file = out / "buildings_osm.geojson"
    edges_file = out / "roads_edges.geojson"
    pois_file = out / "pois_osm.geojson"

    logger.info(f"Saving {bld_file}")
    buildings.to_file(bld_file, driver="GeoJSON")

    logger.info(f"Saving {edges_file}")
    edges.to_file(edges_file, driver="GeoJSON")

    logger.info(f"Saving {pois_file}")
    pois.to_file(pois_file, driver="GeoJSON")

    logger.info("✅ OSM extraction completed successfully.")


if __name__ == "__main__":
    main()
