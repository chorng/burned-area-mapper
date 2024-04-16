import os
from datetime import date, timedelta
from pathlib import Path

from evalscripts import burn_severity_visualisation
from sentinelhub import (
    CRS,
    BBox,
    DataCollection,
    MimeType,
    SentinelHubDownloadClient,
    SentinelHubRequest,
    SHConfig,
    UtmZoneSplitter,
)

# input settings
# AOI = (149.390717, -33.016725, 149.637909, -32.844981)
AOI = (148.79697, -33.20518, 150.05036, -32.64876)
FIRE_START = "2023-03-05"
FIRE_END = "2023-03-19"
TIME_DELTA = timedelta(days=10)
RESOLUTION = 10
MAXCC = 0.3
RESULT_DIR = Path(__file__).parent / ".." / "results"

# configurations
config = SHConfig()
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
config.sh_client_id = os.environ["SH_CLIENT_ID"]
config.sh_client_secret = os.environ["SH_CLIENT_SECRET"]

# split aoi
bbox = BBox(AOI, crs=CRS.WGS84)
utm_zone_splitter = UtmZoneSplitter([bbox.geometry], CRS.WGS84, (20000, 20000))
bbox_list = utm_zone_splitter.get_bbox_list()


# compile requests
def burned_area_map_request(bbox, time_interval, resolution, maxcc, evalscript, result_dir, config):
    return SentinelHubRequest(
        data_folder=result_dir,
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A.define_from("CDSE_S2L2A", service_url=config.sh_base_url),
                time_interval=time_interval,
                maxcc=maxcc,
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=bbox,
        resolution=tuple([resolution] * 2),
        config=config,
    )


time_interval = (
    (date.fromisoformat(FIRE_START) - TIME_DELTA).strftime("%Y-%m-%d"),
    (date.fromisoformat(FIRE_END) + TIME_DELTA).strftime("%Y-%m-%d"),
)
evalscript = burn_severity_visualisation(FIRE_START, FIRE_END)
requests = [
    burned_area_map_request(bbox, time_interval, RESOLUTION, MAXCC, evalscript, RESULT_DIR, config)
    for bbox in bbox_list
]
download_requests = [request.download_list[0] for request in requests]
downloaded_data = SentinelHubDownloadClient(config=config).download(download_requests, max_threads=10)
