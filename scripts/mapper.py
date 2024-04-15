import os
from datetime import date, timedelta
from pathlib import Path

from evalscripts import burn_severity_visualisation
from sentinelhub import CRS, BBox, DataCollection, MimeType, SentinelHubRequest, SHConfig, bbox_to_dimensions

# input settings
AOI = (149.390717, -33.016725, 149.637909, -32.844981)
FIRE_START = "2023-03-05"
FIRE_END = "2023-03-19"
TIME_DELTA = timedelta(days=10)
RESULTS_DIR = Path(__file__).parent / ".." / "results"

# configurations
config = SHConfig()
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
config.sh_client_id = os.environ["SH_CLIENT_ID"]
config.sh_client_secret = os.environ["SH_CLIENT_SECRET"]

# compile requests
bbox = BBox(AOI, crs=CRS.WGS84)
time_interval = (
    (date.fromisoformat(FIRE_START) - TIME_DELTA).strftime("%Y-%m-%d"),
    (date.fromisoformat(FIRE_END) + TIME_DELTA).strftime("%Y-%m-%d"),
)
size = bbox_to_dimensions(bbox, resolution=10)
evalscript = burn_severity_visualisation(FIRE_START, FIRE_END)
request = SentinelHubRequest(
    data_folder=RESULTS_DIR,
    evalscript=evalscript,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A.define_from("CDSE_S2L2A", service_url=config.sh_base_url),
            time_interval=time_interval,
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=size,
    config=config,
)

# download maps
response = request.get_data(save_data=True)
