import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import "./Legend.css";
import "leaflet/dist/leaflet.css";

// Referenced https://codesandbox.io/p/sandbox/how-to-add-a-legend-to-the-map-using-react-leaflet-6yqs5?file=%2Fsrc%2Fstyles.css%3A1%2C1-32%2C1
function Legend() {
  const map = useMap();

  useEffect(() => {
    const getColor = (d) => {
      return d > 104
        ? "#ff0000"
        : d > 78
        ? "#ffa500"
        : d > 52
        ? "#ffff00"
        : d > 26
        ? "#00ffff"
        : d > 0
        ? "#0000ff"
        : "#000000";
    };

    const legend = L.control({ position: "bottomright" });

    legend.onAdd = () => {
      const div = L.DomUtil.create("div", "info legend");
      const grades = [0, 26, 52, 78, 104, 130];
      let labels = [];

      labels.push(
        '<strong>Precipitation (mm/month)</strong><br>'
      )

      for (let i = 0; i < grades.length; i++) {
        const from = grades[i];
        const to = grades[i + 1];

        labels.push(
        `<div><i style="background:${getColor(from + 1)}"></i> ${from}${to ? `&ndash;${to}` : '+'}</div>`
        );

      }

      div.innerHTML = labels.join("<br>");
      return div;
    };

    legend.addTo(map);

    return () => {
      legend.remove();
    };
  }, [map]);

  return null;
}

export default Legend;
