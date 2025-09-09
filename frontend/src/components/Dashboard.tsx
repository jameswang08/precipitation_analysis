import React, { useState } from 'react';
import './Dashboard.css';
import WeatherForm from './WeatherForm';

function Dashboard() {
  const [plotUrls, setPlotUrls] = useState<string[]>([]);

  return (
    <div className="Dashboard">
      <WeatherForm setPlotUrls={setPlotUrls} />
      <div className="Images">
        {plotUrls.map((url, index) => (
          <img key={index} src={url} alt={`Plot ${index + 1}`} />
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
