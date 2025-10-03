import { MapContainer, TileLayer } from "react-leaflet";
import "./InteractiveMap.css";
import "leaflet/dist/leaflet.css";
import GeoTiffLayer from "../GeoTiffLayer";
import Legend from "../Legend/Legend";

function InteractiveMap() {

    return (
        <MapContainer center={[39.8283, -98.5795]} zoom={5} style={{ width: "80vw", height: "80vh" }}>
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; OpenStreetMap contributors'
            />
            <GeoTiffLayer url="/precipitation.tif" />
            <Legend />
        </MapContainer>
    );
}

export default InteractiveMap