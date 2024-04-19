import argparse

from dash import Dash
from layer import build_dash_leaflet_layer, create_geodataframe

parser = argparse.ArgumentParser(
    prog="webapp",
    description="Launch a webapp locally to display burned area.",
)
webapp_parameters = parser.add_argument_group("webapp_parameters")
webapp_parameters.add_argument(
    "-rd",
    "--result-dir",
    help="The parent directory of responses. Should always be under the /app/assets.",
    type=str,
    required=True,
)
parser.parse_args()


def main():
    args = parser.parse_args()
    gdf = create_geodataframe(args.result_dir)
    app = Dash()
    app.layout = build_dash_leaflet_layer(gdf)
    app.run_server()


if __name__ == "__main__":
    main()
