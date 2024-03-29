import { useState } from "react";
import { AQIContext } from "../contexts/AirQualityContext";

// Set up provider with mock data
const TestAQIProvider = (props) => {
    const [site, setSite] = useState({
        "id": 1,
        "name": "Amazon Park - Eugene, OR",
        "latitude": 44.026280,
        "longitude": -123.083715,
    });
    const testTime = "11am Jan 2023";
    const externalData = [1,2,3,4,5,6];
    const forecast = [2,3,4,5,6,7,8,9,10,11,12,11];
    const timeSteps = [
        "11am", "12pm", "1pm", "2pm", "3pm", "4pm", 
        "5pm", "6pm", "7pm", "8pm", "9pm", "10pm"
    ];
    const [currentTime, setCurrentTime] = useState(testTime);
    const [currentData, setCurrentData] = useState(externalData);
    const [forecastData, setForecastData] = useState(forecast);
    const [futureTimeSteps, setFutureTimeSteps] = useState(timeSteps);

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
}

export default TestAQIProvider;