import { useState } from "react";
import { MapContainer, TileLayer } from "react-leaflet";
import "./InteractiveMap.css";
import "leaflet/dist/leaflet.css";
import GeoTiffLayer from "../GeoTiffLayer";
import Legend from "../Legend/Legend";
import InteractiveMapForm from "../InteractiveMapForm";

function InteractiveMap() {
    const [selection, setSelection] = useState({
        model: "NCEP-CFSv2",
        month: "October",
    });

    const geotiffUrl = `/${selection.model}_${selection.month}.tif`;

    console.log("Current selection:", geotiffUrl);

    return (
        <>
            <InteractiveMapForm onSelectionChange={setSelection} />
            <MapContainer center={[39.8283, -98.5795]} zoom={5} style={{ width: "80vw", height: "80vh" }}>
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; OpenStreetMap contributors'
                />
                <GeoTiffLayer url={geotiffUrl} />
                <Legend />
            </MapContainer>
        </>
    );
}

export default InteractiveMap