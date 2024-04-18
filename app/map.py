import argparse
import json
import os
from glob import glob

import dash_leaflet as dl
import geopandas as gpd
import pandas as pd
from dash import Dash
from sentinelhub import CRS, BBox

RESULT_DIR = "./app/assets"

parser = argparse.ArgumentParser(
    prog="webapp",
    description="Launch a webapp locally to display burned area.",
)
webapp_parameters = parser.add_argument_group("webapp_parameters")
webapp_parameters.add_argument(
    "-rd",
    "--result-dir",
    help="The parent directory of responses. Should always be under the /app/assets.",
    type=str,
    required=True,
)
parser.parse_args()


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


args = parser.parse_args()
gdf = create_geodataframe(args.result_dir)
app = Dash()
app.layout = build_dash_leaflet_layer(gdf)


if __name__ == "__main__":
    app.run_server()
