import json
import os
from glob import glob

import dash_leaflet as dl
import geopandas as gpd
import pandas as pd
from sentinelhub import CRS, BBox


def get_responses(result_dir: str) -> list[str]:
    """Get paths to the directories of responses.
    :param result_dir: Path to the directory where result of the requests are saved.
    :return: List of paths.
    """
    return glob(f"{result_dir}/*/")


def read_image_bounds(response: str) -> tuple[list[float], int]:
    """Read bounding box and crs of the response from request metadata.
    :param response: Path to the directory where response is saved.
    :return: Bounding box and coordinate reference system of response.
    """
    request = os.path.join(response, "request.json")
    with open(request, encoding="utf-8") as f:
        request_dict = json.load(f)
    bounds = request_dict["request"]["payload"]["input"]["bounds"]
    bbox = bounds["bbox"]
    crs = int(bounds["properties"]["crs"].split("/")[-1])
    return bbox, crs


def create_geodataframe(result_dir: str) -> gpd.GeoDataFrame:
    """Create a GeoDataFrame for responses.
    :param result_dir: Path to the directory where responses are saved.
    :return: A GeoDataFrame contains bounding box of response and url of its corresponding map in the format of PNG.
    """
    responses = get_responses(result_dir)
    gdf_list = []
    for response in responses:
        bbox, crs = read_image_bounds(response)
        geometry = BBox(bbox, crs=CRS(crs))
        img_url = os.path.join("assets/", response.split("assets/")[-1], "response.png")
        gdf_list.append(
            gpd.GeoDataFrame({"geometry": [geometry.geometry], "img_url": img_url}, crs=geometry.crs.epsg).to_crs(4326)
        )
    return gpd.GeoDataFrame(pd.concat(gdf_list), crs=gdf_list[0].crs)


def build_dash_leaflet_layer(gdf: gpd.GeoDataFrame) -> dl.Map:
    """Create dash leaflet ImageOverlay layer and map container.
    :param gdf: A GeoDataFrame contains maps to be displayed.
    :return: A map container contains all mpas in a GeoDataFrame.
    """
    layers = []
    for row in gdf.itertuples():
        minx, miny, maxx, maxy = row.geometry.bounds
        img_bounds = [[miny, minx], [maxy, maxx]]
        layers += [dl.ImageOverlay(opacity=1, url=row.img_url, bounds=img_bounds), dl.TileLayer()]
    total_minx, total_miny, total_maxx, total_maxy = gdf.total_bounds
    return dl.Map(layers, bounds=[[total_miny, total_minx], [total_maxy, total_maxx]], style={"height": "100vh"})
