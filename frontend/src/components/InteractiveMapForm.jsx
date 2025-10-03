import { useState } from 'react';
import SimpleSelect from './SimpleSelect';

const regions = [
    { value: 'us', label: "United States" }
];

const models = [
    { value: 'NCEP-CFSv2', label: "NCEP-CFSv2" },
    { value: 'ECCC-CanESM5', label: "ECCC-CanESM5" },
    { value: 'ECCC-GEM5.2-NEMO', label: "ECCC-GEM5.2-NEMO" },
    { value: 'NCAR-CESM1', label: "NCAR-CESM1" },
    { value: 'NCAR-CCSM4', label: "NCAR-CCSM4" },
    { value: 'NASA-GEOS-S2S-2', label: "NASA-GEOS-S2S-2" }
];

const lead_times = [
    { value: '0.5', label: "0.5" },
    { value: '1.5', label: "1.5" },
    { value: '2.5', label: "2.5" },
    { value: '3.5', label: "3.5" },
    { value: '4.5', label: "4.5" },
    { value: '5.5', label: "5.5" },
    { value: '6.5', label: "6.5" },
    { value: '7.5', label: "7.5" },
    { value: '8.5', label: "8.5" },
    { value: '9.5', label: "9.5" },
    { value: '10.5', label: "10.5" },
    { value: '11.5', label: "11.5" }
];

const InteractiveMapForm = () => {
    const [selectedRegion, setSelectedRegion] = useState(regions[0].value);
    const [selectedModel, setSelectedModel] = useState(models[0].value);
    const [selectedLeadTime, setSelectedLeadTime] = useState(lead_times[0].value);

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleRegionChange = (value) => setSelectedRegion(value);
    const handleModelChange = (value) => setSelectedModel(value);
    const handleLeadTimeChange = (value) => setSelectedLeadTime(value);

    const handleSubmit = async (e) => {
            e.preventDefault();
            setIsLoading(true);
            setError(null);
    }

    return (
        <div className="WeatherForm">
            <form onSubmit={handleSubmit}>
                <label>
                    Region:
                    <SimpleSelect
                        options={regions}
                        value={selectedRegion}
                        onChange={handleRegionChange}
                    />
                </label>
                <label>
                    Model:
                    <SimpleSelect
                        options={models}
                        value={selectedModel}
                        onChange={handleModelChange}
                    />
                </label>
                <label>
                    Lead Time:
                    <SimpleSelect
                        options={lead_times}
                        value={selectedLeadTime}
                        onChange={handleLeadTimeChange}
                    />
                </label>

                <button type="submit" className="submit-button">Submit</button>
            </form>
            {/* Error Display */}
            {error && (
                <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
                    <strong>Error:</strong> {error}
                </div>
            )}

            {/* Loading Indicator */}
            {isLoading && (
                <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <p className="mt-2 text-gray-600">Generating plots...</p>
                </div>
            )}
        </div>
    );
};

export default InteractiveMapForm;
