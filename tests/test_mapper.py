from datetime import date

import pytest
from sentinelhub import MimeType

from src.evalscripts import burn_severity_visualisation, burned_area_mask


def test_time_interval(mapper_fixture):
    assert date.fromisoformat(mapper_fixture.time_interval[0]) < date.fromisoformat(
        "2023-03-05"
    ), "Request start date is not before the fire start date"
    assert date.fromisoformat(mapper_fixture.time_interval[1]) > date.fromisoformat(
        "2023-03-19"
    ), "Request end date is not after the fire end date"


def test_api_endpoint(mapper_fixture):
    assert mapper_fixture.config.sh_base_url == "https://sh.dataspace.copernicus.eu", "Wrong API endpoint"


def test_token_endpoint(mapper_fixture):
    assert (
        mapper_fixture.config.sh_token_url
        == "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    ), "Wrong token endpint"


@pytest.mark.parametrize(("bbox_size", "expected_num_bbox"), [(20000, 36), (60000, 8)])
def test_split_into_utm_zones(mapper_fixture, bbox_size, expected_num_bbox):
    bbox_list = mapper_fixture.split_into_utm_zones(bbox_size)
    assert len(bbox_list) == expected_num_bbox, "Wrong number of bbox"


@pytest.mark.parametrize(
    ("bbox_size", "evalscript_func", "output_format", "expected_num_request"),
    [
        (20000, burn_severity_visualisation, MimeType.PNG, 36),
        (60000, burned_area_mask, MimeType.TIFF, 8),
    ],
)
def test_create_request_list(mapper_fixture, bbox_size, evalscript_func, output_format, expected_num_request):
    mapper_fixture.split_into_utm_zones(bbox_size)
    request_list = mapper_fixture.create_request_list(evalscript_func, output_format)
    assert len(request_list) == expected_num_request, "Wrong number of request"
