import React, { useState } from 'react';
import './Dashboard.css';
import WeatherForm from './WeatherForm';

function Dashboard() {
  const [plotUrls, setPlotUrls] = useState<string[]>([]);
  const [mapType, setMapType] = useState<string>('plots');

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
        <div>
          Hello World
        </div>
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
