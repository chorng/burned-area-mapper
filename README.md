# Burned Area Mapper

This is a simple burned area mapper built on top of the new launched [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/) and [Sentinel Hub APIs](https://dataspace.copernicus.eu/analyse/apis/sentinel-hub). The mapper takes the area of interest and the fire event time interval as inputs to create a burn area severity visualisation in the format of PNG and/or bruned area binary mask in the format of GeoTIFF or GeoPackage.

The processing pipeline is fully cloud-based and is free of charge. To try the burned area mapper yourself, please [register](https://identity.dataspace.copernicus.eu/auth/realms/CDSE/login-actions/registration?client_id=cdse-public&tab_id=iSAtsRILOlE) to the Copernicus Data Space Ecosystem and create an OAuth client via your [Sentinel Hub dashboard](https://shapps.dataspace.copernicus.eu/dashboard/#/)in the [User setting tab](https://shapps.dataspace.copernicus.eu/dashboard/#/account/settings). The `client_id` and `client_secret` should be parsed to the `burned_area_mapper`.

The mapper uses the delta [Normalised Burned Ratio](https://un-spider.org/advisory-support/recommended-practices/recommended-practice-burn-severity/in-detail/normalized-burn-ratio) to determine the burn severity. The burn severity visualisation displays where the dNBR is greater than 0.27, which indicates moderate-low severity according to the general classification proposed by the United States Geological Survey (USGS). There are three classes in the burn severity visualisation map, which are the moderate-low severity (0.27 <= dNNBR < 0.44), the moderate-high severity (0.44 <= dNNBR < 0.66), and the high severity (dNBR >= 0.66). On the other hand, the burned area map uses 0.27 as the threshold of dNBR to classify burned and unburned areas.

## Project Structure

```
burned-area-mapper/
│
├── .gitignore                    # Gitignore file to specify ignored files and directories
├── .github/workflows             # GitHub CI actions
├── .pre-commit-config.yaml        # Basic pre-commit config file
├── pyproject.toml                # TOML configuration file often used for tool settings and project metadata
├── README.md                     # Project README with an overview and usage instructions
├── requirements.txt              # File listing project dependencies
├── requirements-dev.txt          # File listing project dependencies for development
├── app/                          # Directory for web app
├── src/                          # Directory for source code of mapper
└── tests/                        # Directory for tests
```

## Usage

The mapper is built on top of the Copernicus Data Space Ecosystem. Please follow the [instruction](https://documentation.dataspace.copernicus.eu/Registration.html) to register to the Copernicus Data Space Ecosystem and [authenticate](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Overview/Authentication.html) yourself to enable Sentinel Hub APIs. **Note** that there are [quotas and limitations](https://documentation.dataspace.copernicus.eu/Quotas.html) for a **Copernicus General User**'s usage of Sentinel Hub APIs in Copernicus Data Space Ecosystem.

After OAuth client registration, it will be easy and straightforward to follow the steps below to create either a burn severity visualisation map or a burned area map of the fire event in your area of interest.

### Step 1: Create and Activate a Virtual Environment

```
# Create a virtual environment named "env"
python3 -m venv env

# Activate the virtual environment
# For Linux/MacOs
source env/bin/activate

# For Windows
.\env\Scripts\activate
```

### Step 2: Install Requirements

```
# Ensure you are inside the activated virtual environment
# Install requirements using pip
pip install -r requirements-dev.txt -r requirements.txt
```

### Step 3: Set up Environmental Variables

```
# Make your OAuth client id and client secret environmental variables
export CLIENT_ID=<your-client-id> CLIENT_SECRET=<your-client-secret>
```

### Step 4: Run the Mapper

In the example, we will map the Alpha Road Tambaroora bushfire in NSW Central West, Austria occured between 05.03.2023 and 19.03.2023.

- Create burned area map as a GeoPackage: `python burned_area_mapper.py -b 148.79697 -33.20518 150.05036 -32.64876 -c 4326 -fs "2023-03-05" -fe "2023-03-19" -i $CLIENT_ID -s $CLIENT_SECRET -mt "mask" -rd "./results/gpkg" -r 60 -bs 60000 -gp True`

- Create burn severity visualisatioin as PNG: `python burned_area_mapper.py -b 148.79697 -33.20518 150.05036 -32.64876 -c 4326 -fs "2023-03-05" -fe "2023-03-19" -i $CLIENT_ID -s $CLIENT_SECRET -mt "visualisation" -rd "./app/assets/tambaroora_fire" -r 60 -bs 60000`

- Launch interactive map: `python app/map.py -rd "./app/assets/tambaroora_fire"`

**Note**: Please run `python burned_area_mapper.py --help` for more details about the burned area mapper.
