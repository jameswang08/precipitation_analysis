import { useEffect } from "react";
import { useMap } from "react-leaflet";
import GeoRasterLayer from "georaster-layer-for-leaflet";
import parseGeoraster from "georaster";
// @ts-ignore


type GeoRaster = {
  noDataValue: number | null;
  pixelHeight: number;
  pixelWidth: number;
  numberOfRasters: number;
  projection?: string;
  xmin: number;
  ymax: number;
  xmax: number;
  ymin: number;
  values: number[][][];
  height: number;
  width: number;
  getValues: (...args: any[]) => Promise<number[]>;
};

function GeoTiffLayer({ url }: { url: string }) {
  const map = useMap();

  useEffect(() => {
    fetch(url)
      .then((res) => res.arrayBuffer())
      .then((arrayBuffer) => parseGeoraster(arrayBuffer) as Promise<any>)
      .then((georaster) => {
        const layer = new GeoRasterLayer({
          georaster,
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
      });
  }, [map, url]);

  return null;
}

export default GeoTiffLayer;