import { MapContainer, TileLayer, ImageOverlay } from "react-leaflet";
import "./InteractiveMap.css";
import "leaflet/dist/leaflet.css";
import GeoTiffLayer from "./GeoTiffLayer";
import HeatmapLayer from "./HeatmapLayer";
import { useEffect, useState } from "react";


function InteractiveMap() {
    const [heatData, setHeatData] = useState([]);

    useEffect(() => {
        fetch("/heatmap_data.json")
        .then((res) => res.json())
        .then((data) => {
            const usBounds = {
            latMin: 25,
            latMax: 49,
            lonMin: -125,
            lonMax: -66,
            };

            const usHeatmapData = data.filter(
            ([lat, lon, intensity]: [number, number, number]) =>
                lat >= usBounds.latMin &&
                lat <= usBounds.latMax &&
                lon >= usBounds.lonMin &&
                lon <= usBounds.lonMax
            );

            setHeatData(usHeatmapData);
        });
    }, []);

    return (
        <MapContainer center={[39.8283, -98.5795]} zoom={5} style={{ width: "80vw", height: "80vh" }}>
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; OpenStreetMap contributors'
            />
          <GeoTiffLayer url="/precipitation.tif" />
          {/* <HeatmapLayer points = {heatData}></HeatmapLayer> */}
        </MapContainer>
    );
}

export default InteractiveMap