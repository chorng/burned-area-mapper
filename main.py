import os
import warnings
from pathlib import Path

from src.mapper import BurnedAreaMapper

warnings.filterwarnings("ignore")

BBOX = (148.79697, -33.20518, 150.05036, -32.64876)
CRS = 4326
FIRE_START = "2023-03-05"
FIRE_END = "2023-03-19"
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
RESULT_DIR = Path(__file__).parent / "results"

burned_area_mapper = BurnedAreaMapper(BBOX, CRS, FIRE_START, FIRE_END, CLIENT_ID, CLIENT_SECRET, RESULT_DIR)
burned_area_mapper.split_into_utm_zones((20000, 20000))
burned_area_mapper.create_request_list()
burned_area_mapper.download_requests()
