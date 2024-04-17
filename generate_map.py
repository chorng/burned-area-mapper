import argparse
import warnings

from src.evalscripts import burn_severity_visualisation, burned_area_mask
from src.mapper import BurnedAreaMapper
from src.vectorizer import create_gpkg

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(
    prog="burned-area-mapper",
    description="Visualise burned area and create burned area mask",
)
mapper_parameters = parser.add_argument_group("mapper_parameters")
mapper_parameters.add_argument(
    "-b",
    "--bbox",
    help="The area of interest represented as a bounding box.",
    nargs="+",
    type=float,
    required=True,
)
mapper_parameters.add_argument(
    "-c",
    "--crs",
    help="The coordinate reference system of the bounding box.",
    type=int,
    required=True,
)
mapper_parameters.add_argument(
    "-fs",
    "--fire-start",
    help="The start date of the fire.",
    type=str,
    required=True,
)
mapper_parameters.add_argument(
    "-fe",
    "--fire-end",
    help="The end date of the fire.",
    type=str,
    required=True,
)
mapper_parameters.add_argument(
    "-i",
    "--client-id",
    help="The Copernicus Data Space Ecosystem Sentinel Hub client id.",
    type=str,
    required=True,
)
mapper_parameters.add_argument(
    "-s",
    "--client-secret",
    help="The Copernicus Data Space Ecosystem Sentinel Hub client secret.",
    type=str,
    required=True,
)
mapper_parameters.add_argument(
    "-rd",
    "--result-dir",
    help="The path to the output diretory.",
    type=str,
    required=True,
)
mapper_parameters.add_argument(
    "-m",
    "--map",
    help="Choose from visualisation or mask.",
    type=str,
    required=True,
)
mapper_parameters.add_argument(
    "-r",
    "--resolution",
    help="Resolution in metre.",
    type=int,
    default=10,
    required=False,
)
mapper_parameters.add_argument(
    "-d",
    "--delta-day",
    help="Number of days before and after the fire event to search for available Sentinel-2 scenes.",
    type=int,
    default=10,
    required=False,
)
mapper_parameters.add_argument(
    "-mc",
    "--maxcc",
    help="Maximum cloud coverage of the Sentinel-2 scene.",
    type=float,
    default=0.3,
    required=False,
)
mapper_parameters.add_argument(
    "-bs",
    "--bbox-size",
    help="The size of bbox to be split into",
    type=int,
    default=20000,
    required=False,
)
mapper_parameters.add_argument(
    "-gp",
    "--geopackage",
    help="Vectorize burned area mask and save as GeoPackage",
    type=bool,
    default=False,
    required=False,
)
parser.parse_args()

# BBOX = (148.79697, -33.20518, 150.05036, -32.64876)
# CRS = 4326
# FIRE_START = "2023-03-05"
# FIRE_END = "2023-03-19"
# CLIENT_ID = os.environ["CLIENT_ID"]
# CLIENT_SECRET = os.environ["CLIENT_SECRET"]
# RESULT_DIR = Path(__file__).parent / "results"


class Maps:
    visualisation = burn_severity_visualisation
    mask = burned_area_mask


def main():
    args = parser.parse_args()
    burned_area_mapper = BurnedAreaMapper(
        args.bbox,
        args.crs,
        args.fire_start,
        args.fire_end,
        args.client_id,
        args.client_secret,
        args.result_dir,
        args.delta_day,
        args.resolution,
        args.maxcc,
    )
    burned_area_mapper.split_into_utm_zones(tuple([args.bbox_size] * 2))
    burned_area_mapper.create_request_list(getattr(Maps, args.map))
    burned_area_mapper.download_requests()

    if args.geopackage and args.map == "mask":
        create_gpkg(args.result_dir)


if __name__ == "__main__":
    main()
