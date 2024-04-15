def burn_severity_visualisation(fire_start, fire_end):
    return f"""
        //VERSION=3
        function setup() {{
            return {{
                input: [{{bands: ["B02", "B03", "B04", "B05", "B08", "B12", "SCL"]}}],
                output: {{ bands: 3 }},
                mosaicking: "ORBIT"
            }}
          }}

        function calcNBR(nir, swir) {{
            const denom = nir + swir;
            const nbrval = denom != 0 ? (nir - swir) / denom : NaN;
            return nbrval;
        }}

        // usgs dnbr general classification
        const severity_map = [
            [0.27, 0xfecc5c],
            [0.44, 0xfd8d3c],
            [0.66, 0xe31a1c],
        ];
        const severity_visualizer = new ColorMapVisualizer(severity_map);

        function evaluatePixel(samples) {{
            // calculate delta nbr
            const nbrpre = calcNBR(samples[0].B08, samples[0].B12);
            const nbrpost = calcNBR(samples[1].B08, samples[1].B12);
            const dnbr = nbrpre - nbrpost;

            // mask cloud and water
            const cloud_and_water = [3, 6, 7, 8, 9, 10];
            const is_cloud_or_water = (
                cloud_and_water.includes(samples[0].SCL) ||
                cloud_and_water.includes(samples[1].SCL)
            );

            // set output display layers
            const natural_color = [2.5 * samples[0].B04, 2.5 * samples[0].B03, 2.5 * samples[0].B02];
            let img_vals = dnbr >= 0.27 ? severity_visualizer.process(dnbr) : natural_color
            img_vals = is_cloud_or_water ? natural_color : img_vals;
            return img_vals
        }}

        function preProcessScenes (collections) {{
            const fireStart = "{fire_start}";
            const fireEnd = "{fire_end}";
            const numScenes = collections.scenes.orbits.length;
            collections.scenes.orbits = collections.scenes.orbits.sort(function(a, b) {{
                return new Date(a.dateFrom) - new Date(b.dateFrom);
            }})
            let preFireStartScene = collections.scenes.orbits[0].dateFrom;
            let postFireEndScene = collections.scenes.orbits[numScenes-1].dateFrom;

            // get the nearest scene before the fire
            for (let i = 0; i < numScenes; i++) {{
              currentDate = collections.scenes.orbits[i].dateFrom;
              if (new Date(currentDate) > new Date(preFireStartScene) &&
                  new Date(currentDate) <= new Date(fireStart)
              ) {{
                  preFireStartScene = currentDate;
              }}
            }}

            // get the nearest scene after the fire
            for (let i = numScenes - 1; i > -1; i--) {{
              currentDate = collections.scenes.orbits[i].dateFrom;
              if (new Date(currentDate) < new Date(postFireEndScene) &&
                  new Date(currentDate) >= new Date(fireEnd)
              ) {{
                  postFireEndScene = currentDate;
              }}
            }}
            let allowedDates = [preFireStartScene, postFireEndScene];
            collections.scenes.orbits = collections.scenes.orbits.filter(function (orbit) {{
                let orbitDateFrom = orbit.dateFrom;
                return allowedDates.includes(orbitDateFrom);
            }})
            return collections
          }}
    """
