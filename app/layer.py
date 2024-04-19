import json
import os
from glob import glob

import dash_leaflet as dl
import geopandas as gpd
import pandas as pd
from sentinelhub import CRS, BBox


def get_responses(result_dir):
    return glob(f"{result_dir}/*/")


def read_image_bounds(response):
    request = os.path.join(response, "request.json")
    with open(request, encoding="utf-8") as f:
        request_dict = json.load(f)
    bounds = request_dict["request"]["payload"]["input"]["bounds"]
    bbox = bounds["bbox"]
    crs = bounds["properties"]["crs"].split("/")[-1]
    return bbox, crs


def create_geodataframe(result_dir):
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


def build_dash_leaflet_layer(gdf):
    layers = []
    for row in gdf.itertuples():
        minx, miny, maxx, maxy = row.geometry.bounds
        img_bounds = [[miny, minx], [maxy, maxx]]
        layers += [dl.ImageOverlay(opacity=1, url=row.img_url, bounds=img_bounds), dl.TileLayer()]
    total_minx, total_miny, total_maxx, total_maxy = gdf.total_bounds
    return dl.Map(layers, bounds=[[total_miny, total_minx], [total_maxy, total_maxx]], style={"height": "100vh"})
