import os
import re
from datetime import date
from enum import EnumMeta

import pytest
from sentinelhub import CRS, BBox, SentinelHubRequest, SHConfig

from src.mapper import BurnedAreaMapper


@pytest.mark.parametrize("fixture", ["visualisation_fixture", "mask_fixture"])
def test_init(fixture, request):
    mapper = request.getfixturevalue(fixture)
    assert isinstance(mapper.bbox, BBox), "Wrong instance"
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    assert re.match(date_pattern, mapper.fire_start), "Wrong date pattern"
    assert re.match(date_pattern, mapper.fire_end), "Wrong date pattern"
    assert date.fromisoformat(mapper.time_interval[0]) < date.fromisoformat(
        "2023-03-05"
    ), "Request start date is not before the fire start date"
    assert date.fromisoformat(mapper.time_interval[1]) > date.fromisoformat(
        "2023-03-19"
    ), "Request end date is not after the fire end date"
    assert isinstance(mapper.config, SHConfig), "Wrong instance"
    assert callable(mapper.evalscript_func), "Not callable"
    assert isinstance(type(mapper.img_format), EnumMeta), "Wrong instance"
    assert os.path.isdir(mapper.result_dir), "Not valid path"
    assert isinstance(mapper.resolution, int), "Wrong instance"
    assert isinstance(mapper.maxcc, float), "Wrong instance"


def test_configure():
    config = BurnedAreaMapper.configure("client_id", "client_secret")
    assert config.sh_base_url == "https://sh.dataspace.copernicus.eu", "Wrong endpoint"
    assert (
        config.sh_token_url == "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    ), "Wrong token endpoint"
    assert config.sh_client_id == "client_id", "Wrong client id"
    assert config.sh_client_secret == "client_secret", "Wrong client secret"


@pytest.mark.parametrize(
    ("fixture", "bbox_size", "expected_num_bbox"),
    [
        ("visualisation_fixture", 20000, 36),
        ("mask_fixture", 60000, 8),
    ],
)
def test_split_into_utm_zones(fixture, bbox_size, expected_num_bbox, request):
    mapper = request.getfixturevalue(fixture)
    bbox_list = mapper.split_into_utm_zones(bbox_size)
    assert len(bbox_list) == expected_num_bbox, "Wrong number of bbox"


@pytest.mark.parametrize(
    ("fixture", "bbox"),
    [
        ("visualisation_fixture", [10, 20, 11, 21]),
        ("mask_fixture", [-20, -5, -15, 0]),
    ],
)
def test_build_request(fixture, bbox, request):
    mapper = request.getfixturevalue(fixture)
    sentinelhub_request = mapper.build_request(BBox(bbox, CRS.WGS84))
    assert sentinelhub_request.payload["input"]["bounds"]["bbox"] == bbox
    assert isinstance(sentinelhub_request, SentinelHubRequest)


@pytest.mark.parametrize(
    ("fixture", "bbox_list"),
    [
        ("visualisation_fixture", [[10, 20, 11, 21], [2, 3, 3, 4]]),
        ("mask_fixture", [[-20, -5, -15, 0]]),
    ],
)
def test_create_request_list(fixture, bbox_list, request):
    mapper = request.getfixturevalue(fixture)
    bbox_list = [BBox(bbox, CRS.WGS84) for bbox in bbox_list]
    request_list = mapper.create_request_list(bbox_list)
    assert len(request_list) == len(bbox_list)


@pytest.mark.parametrize(
    ("mapper_fixture", "request_list"),
    [("visualisation_fixture", ["request1_fixture", "request2_fixture"]), ("mask_fixture", ["request1_fixture"])],
)
def test_download_requests(mapper_fixture, request_list, request):
    mapper = request.getfixturevalue(mapper_fixture)
    request_list = [request.getfixturevalue(i) for i in request_list]
    downloaded_data = mapper.download_requests(request_list)
    assert len(downloaded_data) == len(request_list)
