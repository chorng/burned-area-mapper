from datetime import date


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
