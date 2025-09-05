import React, { useState } from 'react';
import './App.css';
import WeatherForm from './components/WeatherForm';

function App() {
  const [plotUrls, setPlotUrls] = useState<string[]>([]);

  return (
    <div className="App">
      <WeatherForm setPlotUrls={setPlotUrls} />
      <div className="Images">
        {plotUrls.length > 0 && (
          <div className="image-grid">
            {plotUrls.map((url, index) => (
              <div key={index} className="image-container">
                <img src={url} alt={`Plot ${index + 1}`} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

