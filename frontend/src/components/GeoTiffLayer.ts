import { useEffect } from "react";
import { useMap } from "react-leaflet";
import GeoRasterLayer from "georaster-layer-for-leaflet";
import parseGeoraster from "georaster";
import * as L from "leaflet";

function GeoTiffLayer({ url }: { url: string }) {
  const map = useMap();

  useEffect(() => {
    let layer: any;

    const loadLayer = async () => {
      const response = await fetch(url);
      const arrayBuffer = await response.arrayBuffer();

      const raster = await parseGeoraster(arrayBuffer) as any;

      layer = new GeoRasterLayer({
        georaster: raster,
        opacity: 0.1,
        resolution: 256,
        pixelValuesToColorFn: (values) => {
          const val = values[0];
          if (val === null) return 'rgba(0,0,0,0)';

          if (val < 0.2) return "#0000ff";   // blue
          if (val < 0.4) return "#00ffff";   // cyan
          if (val < 0.6) return "#ffff00";   // yellow
          if (val < 0.8) return "#ffa500";   // orange
          return "#ff0000";                  // red
        },
      });

      layer.addTo(map);
      map.fitBounds(layer.getBounds());

      map.on("click", async (e: L.LeafletMouseEvent) => {
        const { lat, lng } = e.latlng;

        L.popup()
          .setLatLng(e.latlng)
          .setContent(`
            <strong>Detailed Stats</strong><br />
            <div>
              <span><strong>Lat:</strong> ${lat.toFixed(2)} <strong>Long:</strong> ${lng.toFixed(2)}</span>
              <table style="border-collapse: collapse; margin-top: 8px; font-size: 12px;">
                <thead>
                  <tr>
                    <th style="text-align: left; padding: 4px;">Model</th>
                    <th style="text-align: left; padding: 4px;">Forecast (mm/month)</th>
                    <th style="text-align: left; padding: 4px;">Bias Ratio</th>
                    <th style="text-align: left; padding: 4px;">NRMSE</th>
                    <th style="text-align: left; padding: 4px;">ACC</th>
                    <th style="text-align: left; padding: 4px;">NMAD</th>
                  </tr>
                </thead>
                <tbody>
                  ${[
                    "NCEP-CFSv2",
                    "ECCC-CanESM5",
                    "ECCC-GEM5.2-NEMO",
                    "NCAR-CESM1",
                    "NCAR-CCSM4",
                    "NASA-GEOS-S2S-2"
                  ]
                    .map(
                      (model) => `
                    <tr>
                      <td style="padding: 4px;"><strong>${model}</strong></td>
                      <td style="padding: 4px;">1</td>
                      <td style="padding: 4px;">2</td>
                      <td style="padding: 4px;">3</td>
                      <td style="padding: 4px;">4</td>
                      <td style="padding: 4px;">5</td>
                    </tr>
                  `
                    )
                    .join("")}
                </tbody>
              </table>
            </div>
          `)
          .openOn(map);
      });
    };

    loadLayer();

    return () => {
      if (map && layer) {
        map.off("click");
        map.removeLayer(layer);
      }
    };
  }, [map, url]);

  return null;
}

export default GeoTiffLayer;
