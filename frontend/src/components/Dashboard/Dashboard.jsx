import React, { useState } from 'react';
import './Dashboard.css';
import WeatherForm from '../WeatherForm/WeatherForm';
import InteractiveMap from '../InteractiveMap/InteractiveMap';

function Dashboard() {
  const [plotUrls, setPlotUrls] = useState([]);
  const [mapType, setMapType] = useState('plots');

  let content;

  if (mapType === "plots") {
    content =
      (
        <>
          <WeatherForm setPlotUrls={setPlotUrls} />
          <div className="Images">
            {plotUrls.map((url, index) => (
              <img key={index} src={url} alt={`Plot ${index + 1}`} />
            ))}
          </div>
        </>
      )
  }
  else {
    content =
      (
        <InteractiveMap></InteractiveMap>
      )
  }

  return (
    <div className="Dashboard">
      <button className = "toggleMode" onClick={
        () => {
          if (mapType === "plots"){
            setMapType("interactive")
          }
          else {
            setMapType("plots")
          }
        }
      }>
        Toggle Mode
      </button>
      {content}
    </div>
  );
}

export default Dashboard;
