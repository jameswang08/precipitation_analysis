import { useState } from 'react';
import SimpleSelect from './SimpleSelect';

const regions = [
    { value: 'us', label: "United States" }
];

const models = [
    { value: 'CanCM4i', label: "CanCM4i" }
]

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

const WeatherForm: React.FC = () => {
    const [selectedRegion, setSelectedRegion] = useState<string>(regions[0].value);
    const [selectedModel, setSelectedModel] = useState<string>(models[0].value);
    const [selectedLeadTime, setSelectedLeadTime] = useState<string>(lead_times[0].value);
    const [selectedTimeScale, setSelectedTimeScale] = useState<string>(time_scale[0].value);

    const handleRegionChange = (value: string) => {
        setSelectedRegion(value);
    };

    const handleModelChange = (value: string) => {
        setSelectedModel(value);
    };

    const handleLeadTimeChange = (value: string) => {
        setSelectedLeadTime(value);
    };

    const handleTimeScaleChange = (value: string) => {
        setSelectedTimeScale(value);
    };

    return (
        <div className="WeatherForm">
            <form>
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

            </form>
        </div>
    )
}

export default WeatherForm
