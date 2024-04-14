def burn_severity_visualisation(fire_start, fire_end, moderate_burned_threshold, severe_burned_threshold):
    return f"""
        //VERSION=3
        function setup() {{
            return {{
                input: [{{bands: ["B02", "B03", "B04", "B05", "B08", "B12"]}}],
                output: {{ bands: 3 }},
                mosaicking: "ORBIT"
            }}
          }}

        function stretch(val, min, max) {{return (val - min) / (max - min);}}

        function calcNBR(nir, swir) {{
            var denom = nir + swir;
            var nbrval = denom != 0 ? (nir - swir) / denom : NaN;
            return nbrval;
        }}

        function evaluatePixel(samples) {{
            // calculate delta nbr
            const nbrpre = calcNBR(samples[0].B08, samples[0].B12);
            const nbrpost = calcNBR(samples[1].B08, samples[1].B12);
            const dnbr = nbrpre - nbrpost;

            // set output display layers
            const stretchMin = 0.05;
            const stretchMax = 1.00;
            const naturalColors = [
                stretch(2.8 * samples[0].B04 + 0.1 * samples[0].B05, stretchMin, stretchMax),
                stretch(2.8 * samples[0].B03 + 0.15 * samples[0].B08, stretchMin, stretchMax),
                stretch(2.8 * samples[0].B02, stretchMin, stretchMax)
            ];
            const burnModerate = [
                stretch(2.8 * samples[0].B04 + 0.1 * samples[0].B05, stretchMin,stretchMax)+0.5,
                stretch(2.8 * samples[0].B03 + 0.15 * samples[0].B08, stretchMin, stretchMax)+0.5,
                stretch(2.8 * samples[0].B02, stretchMin, stretchMax)
            ];
            const burnSevere = [
                stretch(2.8 * samples[0].B04 + 0.1 * samples[0].B05, stretchMin, stretchMax)+0.5,
                stretch(2.8 * samples[0].B03 + 0.15 * samples[0].B08, stretchMin, stretchMax),
                stretch(2.8 * samples[0].B02, stretchMin, stretchMax)
            ];
            return (dnbr < {moderate_burned_threshold} || isNaN(dnbr)) ? naturalColors
                : (dnbr < {severe_burned_threshold}) ? burnModerate
                : burnSevere;
        }}

        function preProcessScenes (collections) {{
            const fireStart = {fire_start};
            const fireEnd = {fire_end};
            const numScenes = collections.scenes.orbits.length;
            collections.scenes.orbits = collections.scenes.orbits.sort(function(a, b) {{
                return new Date(a.dateFrom) - new Date(b.dateFrom);
            }})
            var preFireStartScene = collections.scenes.orbits[0].dateFrom;
            var postFireEndScene = collections.scenes.orbits[numScenes-1].dateFrom;

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
            var allowedDates = [preFireStartScene, postFireEndScene];
            collections.scenes.orbits = collections.scenes.orbits.filter(function (orbit) {{
                var orbitDateFrom = orbit.dateFrom;
                return allowedDates.includes(orbitDateFrom);
            }})
            return collections
          }}
    """
