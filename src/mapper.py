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


class BurnedAreaMapper:
    def __init__(
        self,
        bbox,
        crs,
        fire_start,
        fire_end,
        client_id,
        client_secret,
        result_dir,
        delta_day=10,
        resolution=10,
        maxcc=0.3,
    ):
        self.bbox = BBox(bbox, crs=CRS(crs))
        self.time_interval = (
            (date.fromisoformat(fire_start) - timedelta(days=delta_day)).strftime("%Y-%m-%d"),
            (date.fromisoformat(fire_end) + timedelta(days=delta_day)).strftime("%Y-%m-%d"),
        )
        self.fire_start = fire_start
        self.fire_end = fire_end

        def _configure(client_id, client_secret):
            config = SHConfig()
            config.sh_base_url = "https://sh.dataspace.copernicus.eu"
            config.sh_token_url = (
                "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
            )
            config.sh_client_id = client_id
            config.sh_client_secret = client_secret
            return config

        self.config = _configure(client_id, client_secret)
        self.result_dir = result_dir
        self.resolution = resolution
        self.maxcc = maxcc

    def split_into_utm_zones(self, bbox_size):
        utm_zone_splitter = UtmZoneSplitter([self.bbox.geometry], self.bbox.crs, bbox_size)
        self.bbox_list = utm_zone_splitter.get_bbox_list()
        return self.bbox_list

    def create_request_list(self, evalscript_func):
        self.request_list = [
            self.build_request(
                bbox,
                self.time_interval,
                self.resolution,
                self.maxcc,
                evalscript_func(self.fire_start, self.fire_end),
                self.result_dir,
                self.config,
            )
            for bbox in self.bbox_list
        ]
        return self.request_list

    def download_requests(self):
        download_requests = [request.download_list[0] for request in self.request_list]
        return SentinelHubDownloadClient(config=self.config).download(
            download_requests, max_threads=10, show_progress=True
        )

    @staticmethod
    def build_request(bbox, time_interval, resolution, maxcc, evalscript, result_dir, config):
        return SentinelHubRequest(
            data_folder=result_dir,
            evalscript=evalscript,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A.define_from(
                        "CDSE_S2L2A", service_url=config.sh_base_url
                    ),
                    time_interval=time_interval,
                    maxcc=maxcc,
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            resolution=tuple([resolution] * 2),
            config=config,
        )
