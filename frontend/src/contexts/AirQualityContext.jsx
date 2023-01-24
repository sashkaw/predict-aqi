import { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";
import dayjs from "dayjs";
import dayjsPluginUTC from "dayjs-plugin-utc";
dayjs.extend(dayjsPluginUTC)

export const AQIContext = createContext();
export const useAQIContext = () => useContext(AQIContext);

export const AQIProvider = (props) => {
    const refreshInterval = 1000 * 60 * 60; // Every hour
    const dateFormat = "h a MMM D";
    // Get current time so we know when to refresh the forecast
    const [nowTime, setNowTime] = useState(dayjs().format(dateFormat));
    // Helper function to update the current time
    const refreshClock = () => {
        setNowTime(dayjs().format(dateFormat));
    }

    // Set up additional state variables
    const [site, setSite] = useState({
        "id": 1,
        "name": "Amazon Park - Eugene, OR",
        "latitude": 44.026280,
        "longitude": -123.083715,
      });
    
    const [currentTime, setCurrentTime] = useState(dayjs().format(dateFormat));
    const [currentData, setCurrentData] = useState(null);
    const [forecastData, setForecastData] = useState([]);
    const [futureTimeSteps, setFutureTimeSteps] = useState([]);

    // Set up timer to refresh current time stamp
    useEffect(() => {
        const timerId = setInterval(refreshClock, refreshInterval);
        return function cleanup() {
          clearInterval(timerId);
        };
      }, [nowTime]);

    // Fetch AQI data from backend
    // at a given refresh interval
    useEffect(() => {
        //console.log("axios:", nowTime);
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
        //}
    }, [nowTime]); // Only run if value of current time changes

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



