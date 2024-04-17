import pytest

from src.mapper import BurnedAreaMapper


@pytest.fixture(scope="session")
def mapper_fixture():
    return BurnedAreaMapper(
        (148.79697, -33.20518, 150.05036, -32.64876),
        4326,
        "2023-03-05",
        "2023-03-19",
        "fakeclientid",
        "fackclientsecret",
        "test_result_dir",
    )
