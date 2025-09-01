import { useState } from 'react';
import SimpleSelect from './SimpleSelect';

const regions = [
    { value: 'us', label: "United States" }
];

const models = [
    { value: 'CanCM4i', label: "CanCM4i" }
]

const lead_time =
    Array.from(
        { length: Math.floor((11.5 - 0.5) / 1) + 1 },
        (_, i) => 0.5 + i * 1
    );

const time_scale = [
    { value: 'monthly', label: "Monthly" },
    { value: 'seasonal', label: "Seasonal" }
];

const WeatherForm: React.FC = () => {
    const [selectedRegion, setSelectedRegion] = useState<string>(regions[0].value);

    const handleRegionChange = (value: string) => {
        setSelectedRegion(value);
    };

    return (
        <div className="WeatherForm">
            <form>
                <label>
                    Select a region:
                    <SimpleSelect
                        options={regions}
                        value={selectedRegion}
                        onChange={handleRegionChange}
                    />
                </label>
            </form>
        </div>
    )
}

export default WeatherForm
