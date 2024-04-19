from dash_leaflet import Map
from geopandas import GeoDataFrame
from shapely import wkt

from app.layer import build_dash_leaflet_layer, create_geodataframe, get_responses, read_image_bounds


def test_get_responses():
    responses = get_responses("tests/results/")
    assert len(responses) == 2, "Wrong number of response"


def test_read_image_bounds():
    bbox, crs = read_image_bounds("tests/results/assets/6c83e856af8421020dd3a6fec2514cf4/")
    assert bbox == [660000, 6360000, 720000, 6420000], "Wrong bounding box"
    assert crs == "32755", "Wrong coordinate reference system"


def test_create_geodataframe():
    gdf = create_geodataframe("tests/results/assets/")
    assert len(gdf) == 1, "Wrong number of feature"
    assert gdf.crs == 4326, "Wrong coordinate reference system"
    assert gdf.img_url.iloc[0] == "assets/6c83e856af8421020dd3a6fec2514cf4/response.png", "Wrong image url"


def test_build_dash_leaflet_layer():
    gdf = GeoDataFrame(
        {
            "geometry": [
                wkt.loads(
                    "POLYGON ((12.44693 41.870072,12.541001 41.870072,12.541001 41.917096,12.44693 41.917096,12.44693"
                    " 41.870072))"
                ),
                wkt.loads(
                    "POLYGON ((12.540965 41.895105,12.599979 41.893593,12.601999 41.941039,12.54294 41.942553,12.540965"
                    " 41.895105))"
                ),
            ],
            "img_url": [
                "assets/6c83e856af8421020dd3a6fec2514cf4/response.png",
                "assets/04b2eb039f29c815d61d661f25a740a3/response.png",
            ],
        },
        crs=4326,
    )
    container = build_dash_leaflet_layer(gdf)
    assert isinstance(container, Map)
