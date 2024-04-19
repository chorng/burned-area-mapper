import os

from geopandas import GeoDataFrame

from src.vectorizer import create_gpkg, vectorize


def test_vectorize():
    gdf = vectorize("tests/results/mask/response.tiff")
    assert isinstance(gdf, GeoDataFrame)
    assert gdf.crs == 4326
    assert len(gdf) == 4460


def test_create_gpkg():
    result_dir = "tests/results/"
    create_gpkg(result_dir)
    assert os.path.exists(os.path.join(result_dir, "burned_areas.gpkg"))
