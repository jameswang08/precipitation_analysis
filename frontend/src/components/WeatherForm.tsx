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
    { value: 'jan', label: 'January' },
    { value: 'feb', label: 'February' },
    { value: 'mar', label: 'March' },
    { value: 'apr', label: 'April' },
    { value: 'may', label: 'May' },
    { value: 'jun', label: 'June' },
    { value: 'jul', label: 'July' },
    { value: 'aug', label: 'August' },
    { value: 'sep', label: 'September' },
    { value: 'oct', label: 'October' },
    { value: 'nov', label: 'November' },
    { value: 'dec', label: 'December' },
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

    const handleRegionChange = (value: string) => setSelectedRegion(value);
    const handleModelChange = (value: string) => setSelectedModel(value);
    const handleLeadTimeChange = (value: string) => setSelectedLeadTime(value);
    const handleTimeScaleChange = (value: string) => setSelectedTimeScale(value);
    const handleMonthChange = (value: string) => setSelectedMonth(value);
    const handleSeasonChange = (value: string) => setSelectedSeason(value);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        const requestBody: any = {
            region: selectedRegion,
            model: selectedModel,
            lead_time: selectedLeadTime,
            time_scale: selectedTimeScale
        };

        if (selectedTimeScale === 'monthly') {
            requestBody.month = selectedMonth;
        } else if (selectedTimeScale === 'seasonal') {
            requestBody.season = selectedSeason;
        }

        fetch('http://localhost:5000/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        })
            .then(res => res.json())
            .then(data => {
                console.log('Submitted successfully:', data);
            })
            .catch(err => {
                console.error('Submission error:', err);
            });
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
        </div>
    );
};

export default WeatherForm;
