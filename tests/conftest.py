import pytest
from sentinelhub import CRS, BBox, DataCollection, MimeType, SentinelHubRequest, SHConfig

from src.mapper import BurnedAreaMapper

CONFIG = SHConfig("burned-area-mapper")
EVALSCRIPT = """
    //VERSION=3
    function setup() {
        return {
            input: ["B02", "B03", "B04"],
            output: { bands: 3 }
        };
    }

    function evaluatePixel(sample) {
        return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
    }
"""


@pytest.fixture(scope="class")
def visualisation_fixture():
    input_parameters = {
        "bbox": (148.79697, -33.20518, 150.05036, -32.64876),
        "crs": 4326,
        "fire_start": "2023-03-05",
        "fire_end": "2023-03-19",
        "client_id": CONFIG.sh_client_id,
        "client_secret": CONFIG.sh_client_secret,
        "map_type": "visualisation",
        "result_dir": "./tests/results/visualisation",
    }
    return BurnedAreaMapper(**input_parameters)


@pytest.fixture(scope="class")
def mask_fixture():
    input_parameters = {
        "bbox": (148.79697, -33.20518, 150.05036, -32.64876),
        "crs": 4326,
        "fire_start": "2023-03-05",
        "fire_end": "2023-03-19",
        "client_id": CONFIG.sh_client_id,
        "client_secret": CONFIG.sh_client_secret,
        "map_type": "mask",
        "result_dir": "./tests/results/mask",
    }
    return BurnedAreaMapper(**input_parameters)


@pytest.fixture(scope="class")
def request1_fixture():
    return SentinelHubRequest(
        evalscript=EVALSCRIPT,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A.define_from("CDSE_S2L2A", service_url=CONFIG.sh_base_url),
                time_interval=("2024-03-18", "2024-04-18"),
            ),
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.JPG),
        ],
        bbox=BBox([12.482184, 41.894135, 12.483843, 41.895361], CRS.WGS84),
        size=[100, 100],
        config=CONFIG,
    )


@pytest.fixture(scope="class")
def request2_fixture():
    return SentinelHubRequest(
        evalscript=EVALSCRIPT,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A.define_from("CDSE_S2L2A", service_url=CONFIG.sh_base_url),
                time_interval=("2023-10-18", "2023-11-18"),
            ),
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.JPG),
        ],
        bbox=BBox([145.538362, -33.479368, 145.539526, -33.4784], CRS.WGS84),
        size=[100, 100],
        config=CONFIG,
    )
