import { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";
import dayjs from "dayjs";
import dayjsPluginUTC from "dayjs-plugin-utc";
dayjs.extend(dayjsPluginUTC)

export const AQIContext = createContext();
export const useAQIContext = () => useContext(AQIContext);

export const AQIProvider = (props) => {
    const [site, setSite] = useState({
        "id": 1,
        "name": "Amazon Park - Eugene, OR",
        "latitude": 44.026280,
        "longitude": -123.083715,
      });
    
      // TODO: Add watchdog to refresh data when we reach the next time step
      // and possibly update time to refresh automatically
    const dateFormat = "h a MMM D";
    const [currentTime, setCurrentTime] = useState(dayjs().format(dateFormat));
    const [currentData, setCurrentData] = useState(null);
    const [forecastData, setForecastData] = useState([]);
    const [futureTimeSteps, setFutureTimeSteps] = useState([]);

    // Fetch AQI data from backend after DOM has updated
    useEffect(() => {
        axios('/aqi/')
            .then((response) => {
                //console.log(response.data.aqi_current.at(-1))
                // Get most recent AQI observation
                setCurrentData(response.data.aqi_current.at(-1));
                // Get forecasted AQI for future time steps
                setForecastData(response.data.aqi_forecast);
                // Get corresponding time steps for forecasted data
                const futureTimeStepsUTC = response.data.future_timesteps;
                // Convert time stamps to local time
                const futureTimeStepsLocal = [];
                futureTimeStepsUTC.map((item, index) => {
                    const localTime = dayjs.utc(item).local().format(dateFormat);
                    futureTimeStepsLocal.push(localTime);
                })
                setFutureTimeSteps(futureTimeStepsLocal);
            });
    }, [site]); // Only run if value of site changes
    //console.log(futureTimeSteps, currentData)

    return (
        <AQIContext.Provider
            value={{
                site, 
                setSite,
                currentTime,
                setCurrentTime,
                currentData,
                setCurrentData,
                forecastData,
                setForecastData,
                futureTimeSteps,
                setFutureTimeSteps,
            }}
            >
                {props.children}
            </AQIContext.Provider>
    );

};



