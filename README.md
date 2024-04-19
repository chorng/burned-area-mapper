# burned-area-mapper

Create GeoPackage showing burned area: `python burned_area_mapper.py -b 148.79697 -33.20518 150.05036 -32.64876 -c 4326 -fs "2023-03-05" -fe "2023-03-19" -i $CLIENT_ID -s $CLIENT_SECRET -mt "mask" -rd "./results/gpkg" -r 60 -bs 60000 -gp True`

Create burned area visualisatioin: `python burned_area_mapper.py -b 148.79697 -33.20518 150.05036 -32.64876 -c 4326 -fs "2023-03-05" -fe "2023-03-19" -i $CLIENT_ID -s $CLIENT_SECRET -mt "visualisation" -rd "./app/assets/test1" -r 60 -bs 60000`

Launch interactive map: `python app/map.py -rd "./app/assets/test1"`
