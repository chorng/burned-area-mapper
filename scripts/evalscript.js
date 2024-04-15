//VERSION=3
function setup() {
  return {
    input: [{bands: ["B02", "B03", "B04", "B05", "B08", "B12", "SCL"]}],
    output: { bands: 3 },
    mosaicking: "ORBIT"
  }
}

function calcNBR(nir, swir) {
  var denom = nir+swir;
  var nbrval = denom != 0 ? (nir-swir) / denom : NaN;
  return nbrval;
}

const severityMap = [
  [0.27, 0xfecc5c],
  [0.44, 0xfd8d3c],
  [0.66, 0xe31a1c],
];
const severityVisualizer = new ColorMapVisualizer(severityMap);

function evaluatePixel(samples) {
  // calculate dnbr
  const nbrpre = calcNBR(samples[0].B08, samples[0].B12);
  const nbrpost = calcNBR(samples[1].B08, samples[1].B12);
  const dnbr = nbrpre - nbrpost;

  // mask cloud and water
  const sclCloudWater = [3, 6, 7, 8, 9, 10];
  const is_cloud_or_water = (sclCloudWater.includes(samples[0].SCL) || sclCloudWater.includes(samples[1].SCL));

  // set output display layers
  const natural_color = [2.5 * samples[0].B04, 2.5 * samples[0].B03, 2.5 * samples[0].B02];
  let imgVals = dnbr >= 0.27 ? severityVisualizer.process(dnbr) : natural_color
  imgVals = is_cloud_or_water ? natural_color : imgVals;
  return imgVals
}

function preProcessScenes (collections) {
    const fireStart = "2023-03-05";
    const fireEnd = "2023-03-19"
    const numScenes = collections.scenes.orbits.length;
    collections.scenes.orbits = collections.scenes.orbits.sort(function(a, b) {
      return new Date(a.dateFrom) - new Date(b.dateFrom);
    })
    var preFireStartScene = collections.scenes.orbits[0].dateFrom;
    var postFireEndScene = collections.scenes.orbits[numScenes-1].dateFrom;
    for (let i = 0; i < numScenes; i++) {
      currentDate = collections.scenes.orbits[i].dateFrom;
      if (new Date(currentDate) > new Date(preFireStartScene) && new Date(currentDate) <= new Date(fireStart)) {
        preFireStartScene = currentDate;
      }
    }
    for (let i = numScenes - 1; i > -1; i--) {
      currentDate = collections.scenes.orbits[i].dateFrom;
      if (new Date(currentDate) < new Date(postFireEndScene) && new Date(currentDate) >= new Date(fireEnd)) {
        postFireEndScene = currentDate;
      }
    }
    var allowedDates = [preFireStartScene, postFireEndScene];
    collections.scenes.orbits = collections.scenes.orbits.filter(function (orbit) {
        var orbitDateFrom = orbit.dateFrom;
        return allowedDates.includes(orbitDateFrom);
    })
    return collections
  }
//https://sentinelshare.page.link/o2Vh
