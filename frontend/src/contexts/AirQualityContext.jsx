import { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

export const AQIContext = createContext();
export const useAQIContext = () => useContext(AQIContext);

export const AQIProvider = (props) => {
    const [currentData, setCurrentData] = useState([]);
    const [forecastData, setForecastData] = useState([]);

    // Fetch AQI data from backend after DOM has updated
    useEffect(() => {
        axios('/aqi/')
            .then(({response}) => {
                setCurrentData(response.current);
                setForecastData(response.forecast);
            });
    });

    return (
        <AQIContext.Provider
            value={{
                currentData,
                setCurrentData,
                forecastData,
                setForecastData,
            }}
            >
                {props.children}
            </AQIContext.Provider>
    );

};



