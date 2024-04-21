import json
from glob import glob

import geopandas as gpd
import pandas as pd
import rasterio as rio
from rasterio.features import shapes
from shapely.geometry import shape


def vectorize(tiff: str) -> gpd.GeoDataFrame:
    """Vectorize burn area binary mask.
    :param tiff: Path to the tiff file.
    :return: A GeoDataFrame contains polygons of areas where pixel value is 1 in EPSG:4326.
    """
    with rio.open(tiff) as data:
        array = data.read()
        transform = data.transform
        crs = data.crs
    polygon_value_pairs = list(shapes(array, mask=array, transform=transform))
    gdf = gpd.GeoDataFrame(
        {"geometry": [shape(json.loads(json.dumps(pair[0]))) for pair in polygon_value_pairs]}, crs=crs
    )
    return gdf.to_crs(4326)


def create_gpkg(result_dir: str) -> None:
    """Create a GeoPackage from tiff files.
    :param result_dir: Path to the directory where GeoPackage will be saved.
    """
    tiff_list = glob(f"{result_dir}/**/*.tiff")
    gdf_list = [vectorize(tiff) for tiff in tiff_list]
    concat_gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True), crs=gdf_list[0].crs)
    concat_gdf.to_file(f"{result_dir}/burned_areas.gpkg", driver="GPKG")
