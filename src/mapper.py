from datetime import date, timedelta
from typing import Any

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

from src.evalscripts import burn_severity_visualisation, burned_area_mask


class Evalscripts:
    """Class used for the creation of evalscripts of different map types."""

    visualisation = burn_severity_visualisation
    mask = burned_area_mask


class ImgFormats:
    """Class used for the selection of image format of different map types."""

    visualisation = MimeType.PNG
    mask = MimeType.TIFF


class BurnedAreaMapper:
    """The main class to request burned area maps by UTM zones."""

    def __init__(
        self,
        bbox: tuple[float],
        crs: int,
        fire_start: str,
        fire_end: str,
        client_id: str,
        client_secret: str,
        map_type: str,
        result_dir: str,
        delta_day: int = 10,
        resolution: int = 10,
        maxcc: float = 0.3,
    ):
        """
        :param bbox: A tuple of (minx, miny, maxx, maxy) representing a bounding box.
        :param crs: Coordinate reference system of the bounding box in EPSG code.
        :param fire_start: Start date of the fire event.
        :param fire_end: End date of the fire event.
        :param client_id: User's OAuth client id for Sentinel Hub services.
        :param client_secret: User's OAuth client secret for Sentinel Hub services.
        :param map_type: Select a map type from available maps. Either visualisation or mask.
        :param result_dir: Location of the directory where the downloaded map will be saved.
        :param delta_day: Number of days before/after the fire event whose acquisitions are
            allowed to be used for burned area mapping. Default is 10 days.
        :param resolution: Resolution of the map. Default is 10 m.
        :param maxcc: Maximum cloud coverage of acquisitions allowed to be used for
            burned area mapping. Accepts value from 0 to 1. Default is 0.3.
        """
        self.bbox = BBox(bbox, crs=CRS(crs))
        self.fire_start = fire_start
        self.fire_end = fire_end
        self.time_interval = (
            (date.fromisoformat(fire_start) - timedelta(days=delta_day)).strftime("%Y-%m-%d"),
            (date.fromisoformat(fire_end) + timedelta(days=delta_day)).strftime("%Y-%m-%d"),
        )
        self.config = self.configure(client_id, client_secret)
        self.evalscript_func = getattr(Evalscripts, map_type)
        self.img_format = getattr(ImgFormats, map_type)
        self.result_dir = result_dir
        self.resolution = resolution
        self.maxcc = maxcc

    @staticmethod
    def configure(client_id: str, client_secret: str) -> SHConfig:
        """Configure to the Sentinel Hub of Copernicus Data Space Ecosystem deployment.
        :param client_id: User's OAuth client id for Sentinel Hub services.
        :param client_secret: User's OAuth client secret for Sentinel Hub services.
        :return: A `SHConfig` class with configuration parameters.
        """
        config = SHConfig()
        config.sh_base_url = "https://sh.dataspace.copernicus.eu"
        config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        config.sh_client_id = client_id
        config.sh_client_secret = client_secret
        return config

    def split_into_utm_zones(self, bbox_size: tuple[int, int]) -> list[BBox]:
        """Split area according to UTM zones in specified size.
        :param bbox_size: Parameter that describes the shape in which the area will be split. It should be
            a tuple of the form `(n, m)` which means the area bounding box will be split into `n` columns
            and `m` rows.
        :return: A list of bounding boxes.
        """
        utm_zone_splitter = UtmZoneSplitter([self.bbox.geometry], self.bbox.crs, bbox_size)
        return utm_zone_splitter.get_bbox_list()

    def build_request(self, bbox: BBox) -> SentinelHubRequest:
        """Build Sentinel Hub request for burned area map.
        :param bbox: Bounding box of the map.
        :return: Sentinel Hub request of the burned area map.
        """
        return SentinelHubRequest(
            data_folder=self.result_dir,
            evalscript=self.evalscript_func(self.fire_start, self.fire_end),
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A.define_from(
                        "CDSE_S2L2A", service_url=self.config.sh_base_url
                    ),
                    time_interval=self.time_interval,
                    maxcc=self.maxcc,
                )
            ],
            responses=[SentinelHubRequest.output_response("default", self.img_format)],
            bbox=bbox,
            resolution=tuple([self.resolution] * 2),
            config=self.config,
        )

    def create_request_list(self, bbox_list: list[BBox]) -> list[SentinelHubRequest]:
        """Create a list of Sentinel Hub requests of the burned area map.
        :param bbox_list: List of bounding boxes.
        :return: List of Sentinel Hub requests.
        """
        return [self.build_request(bbox) for bbox in bbox_list]

    def download_requests(self, request_list: list[SentinelHubRequest]) -> list[dict[str, Any]]:
        """Make requests and download results.
        :param request_list: List of Sentinel Hub requests.
        :return: List of responses in a dictionary.
        """
        download_requests = [request.download_list[0] for request in request_list]
        return SentinelHubDownloadClient(config=self.config).download(
            download_requests, max_threads=10, show_progress=True
        )
