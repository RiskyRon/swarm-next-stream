// frontend/components/CustomWeatherCard.tsx

import React from 'react';

interface WeatherData {
  location: string;
  temperature_c: string;
  temperature_f: string;
  condition: string;
  icon_url?: string;
  humidity?: string;
  wind_kph?: string;
  wind_mph?: string;
  last_updated?: string;
  [key: string]: any;
}

interface CustomWeatherCardProps {
  data: WeatherData;
}

export const CustomWeatherCard: React.FC<CustomWeatherCardProps> = ({ data }) => (
  <div className="p-4 bg-secondary text-secondary-foreground rounded-md border">
    <h2 className="text-lg font-bold">{data.location}</h2>
    <div className="flex items-center mt-2">
      {data.icon_url && (
        <img
          src={data.icon_url}
          alt={data.condition}
          className="w-16 h-16 mr-4"
        />
      )}
      <div>
        <p className="text-4xl font-bold">{data.temperature_c}</p>
        <p className="capitalize">{data.condition}</p>
      </div>
    </div>
    {/* Additional weather details */}
    <div className="mt-2">
      {data.humidity && <p>Humidity: {data.humidity}</p>}
      {data.wind_kph && <p>Wind: {data.wind_kph}</p>}
      {data.last_updated && <p>Last Updated: {data.last_updated}</p>}
    </div>
  </div>
);

export default CustomWeatherCard;
