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
        let { lat, lng } = e.latlng;

        const requestBody: any = {
            lat: lat,
            lng: lng,
        };

      try {
        const response = await fetch('http://localhost:8000/stats', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.statusText}`);
        }

        const data: Record<string, string | null> = await response.json();

        const formattedValues = Object.entries(data).length > 0
          ? `<ul>${Object.entries(data)
              .map(([key, value]) => `<li><strong>${key}:</strong> ${value ?? "No data"}</li>`)
              .join("")}</ul>`
          : "No data";

        L.popup()
          .setLatLng(e.latlng)
          .setContent(`
            <strong>Detailed Stats</strong><br />
            Lat: ${lat.toFixed(3)}<br />
            Lng: ${lng.toFixed(3)}<br />
            ${formattedValues}
          `)
          .openOn(map);
        } catch (err) {
          console.error("Error getting pixel value:", err);
          L.popup()
            .setLatLng(e.latlng)
            .setContent(`
              <strong>Error</strong><br />
              Lat: ${lat.toFixed(5)}<br />
              Lng: ${lng.toFixed(5)}<br />
              Failed to fetch data.
            `)
            .openOn(map);
        }
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
