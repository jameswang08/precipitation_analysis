import { useState } from 'react';
import SimpleSelect from './SimpleSelect';
import './WeatherForm.css';

const regions = [
    { value: 'us', label: "United States" }
];

const models = [
    { value: 'CanCM4i', label: "CanCM4i" }
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

const time_scale = [
    { value: 'monthly', label: "Monthly" },
    { value: 'seasonal', label: "Seasonal" }
];

const months = [
    { value: 'Jan', label: 'January' },
    { value: 'Feb', label: 'February' },
    { value: 'Mar', label: 'March' },
    { value: 'Apr', label: 'April' },
    { value: 'May', label: 'May' },
    { value: 'Jun', label: 'June' },
    { value: 'Jul', label: 'July' },
    { value: 'Aug', label: 'August' },
    { value: 'Sep', label: 'September' },
    { value: 'Oct', label: 'October' },
    { value: 'Nov', label: 'November' },
    { value: 'Dec', label: 'December' },
];

const seasons = [
    { value: 'Jan-Mar', label: 'Jan-Mar' },
    { value: 'Apr-Jun', label: 'Apr-Jun' },
    { value: 'Jul-Sep', label: 'Jul-Sep' },
    { value: 'Oct-Dec', label: 'Oct-Dec' },
];

const WeatherForm: React.FC = () => {
    const [selectedRegion, setSelectedRegion] = useState(regions[0].value);
    const [selectedModel, setSelectedModel] = useState(models[0].value);
    const [selectedLeadTime, setSelectedLeadTime] = useState(lead_times[0].value);
    const [selectedTimeScale, setSelectedTimeScale] = useState(time_scale[0].value);

    const [selectedMonth, setSelectedMonth] = useState<string>(months[0].value);
    const [selectedSeason, setSelectedSeason] = useState<string>(seasons[0].value);

    const [plotUrls, setPlotUrls] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleRegionChange = (value: string) => setSelectedRegion(value);
    const handleModelChange = (value: string) => setSelectedModel(value);
    const handleLeadTimeChange = (value: string) => setSelectedLeadTime(value);
    const handleTimeScaleChange = (value: string) => setSelectedTimeScale(value);
    const handleMonthChange = (value: string) => setSelectedMonth(value);
    const handleSeasonChange = (value: string) => setSelectedSeason(value);

    const handleSubmit = async (e: React.FormEvent) => {
            e.preventDefault();
            setIsLoading(true);
            setError(null);
            setPlotUrls([]); // Clear previous plots

            const requestBody: any = {
                region: selectedRegion,
                model: selectedModel,
                lead_time: selectedLeadTime,
                time_scale: selectedTimeScale
            };

            if (selectedTimeScale === 'monthly') {
                requestBody.month = selectedMonth;
            } else if (selectedTimeScale === 'seasonal') {
                requestBody.month = selectedSeason;
            }

            try {
                const response = await fetch('http://localhost:8000/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestBody),
                });
                
                const data = await response.json();
                
                if (data.success) {
                    console.log('Submitted successfully:', data);
                    // Convert relative paths to full URLs
                    const fullUrls = data.plots.map((url: string) => 
                        `http://localhost:8000${url}`
                    );
                    setPlotUrls(fullUrls);
                } else {
                    setError(data.error || 'Unknown error occurred');
                }
            } catch (err) {
                console.error('Submission error:', err);
                setError('Failed to submit request');
            } finally {
                setIsLoading(false);
            }
        };

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
                <label>
                    Time Scale:
                    <SimpleSelect
                        options={time_scale}
                        value={selectedTimeScale}
                        onChange={handleTimeScaleChange}
                    />
                </label>

                {/* Conditionally render month or season select */}
                {selectedTimeScale === 'monthly' && (
                    <label>
                        Month:
                        <SimpleSelect
                            options={months}
                            value={selectedMonth}
                            onChange={handleMonthChange}
                        />
                    </label>
                )}
                {selectedTimeScale === 'seasonal' && (
                    <label>
                        Season:
                        <SimpleSelect
                            options={seasons}
                            value={selectedSeason}
                            onChange={handleSeasonChange}
                        />
                    </label>
                )}

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

            {/* Plot Display */}
            {plotUrls.length > 0 && (
                <div>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">
                        Analysis Results ({plotUrls.length} plots)
                    </h2>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {plotUrls.map((url, index) => (
                            <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                                <img 
                                    src={url} 
                                    alt={`Weather plot ${index + 1}`}
                                    className="w-full h-auto rounded shadow-sm"
                                    onError={() => {
                                        console.error(`Failed to load image: ${url}`);
                                    }}
                                />
                                <p className="text-xs text-gray-500 mt-2 break-all">{url}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default WeatherForm;
