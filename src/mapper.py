from datetime import date, timedelta

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
    visualisation = burn_severity_visualisation
    mask = burned_area_mask


class ImgFormats:
    visualisation = MimeType.PNG
    mask = MimeType.TIFF


class BurnedAreaMapper:
    def __init__(
        self,
        bbox,
        crs,
        fire_start,
        fire_end,
        client_id,
        client_secret,
        map_type,
        result_dir,
        delta_day=10,
        resolution=10,
        maxcc=0.3,
    ):
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
    def configure(client_id, client_secret):
        config = SHConfig()
        config.sh_base_url = "https://sh.dataspace.copernicus.eu"
        config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        config.sh_client_id = client_id
        config.sh_client_secret = client_secret
        return config

    def split_into_utm_zones(self, bbox_size):
        utm_zone_splitter = UtmZoneSplitter([self.bbox.geometry], self.bbox.crs, bbox_size)
        return utm_zone_splitter.get_bbox_list()

    def build_request(self, bbox):
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

    def create_request_list(self, bbox_list):
        return [self.build_request(bbox) for bbox in bbox_list]

    def download_requests(self, request_list):
        download_requests = [request.download_list[0] for request in request_list]
        return SentinelHubDownloadClient(config=self.config).download(
            download_requests, max_threads=10, show_progress=True
        )
