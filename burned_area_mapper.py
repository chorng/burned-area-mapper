import argparse
import warnings

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
    "-mt",
    "--map-type",
    help="Choose from visualisation or mask.",
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


def main():
    args = parser.parse_args()
    burned_area_mapper = BurnedAreaMapper(
        tuple(args.bbox),
        args.crs,
        args.fire_start,
        args.fire_end,
        args.client_id,
        args.client_secret,
        args.map_type,
        args.result_dir,
        args.delta_day,
        args.resolution,
        args.maxcc,
    )
    bbox_list = burned_area_mapper.split_into_utm_zones(tuple([args.bbox_size] * 2))
    request_list = burned_area_mapper.create_request_list(bbox_list)
    _ = burned_area_mapper.download_requests(request_list)

    if args.geopackage and args.map_type == "mask":
        create_gpkg(args.result_dir)


if __name__ == "__main__":
    main()
