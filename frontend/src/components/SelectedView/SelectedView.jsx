import { useAQIContext } from "../../contexts/AirQualityContext";
import { HiOutlineLocationMarker } from "react-icons/hi";
import dayjs from "dayjs";

export function SelectedView() {
    // Get current AQI and forecast AQI
    const { currentData, forecastData } = useAQIContext();

    // Show loading message if waiting for data
    if(!currentData & !forecastData) return <div>Loading...</div>

    // Get current time
    let dt = DateTime.local();
    let currentTime = dt.toLocaleString(DateTime.DATETIME_MED);

    // Get forecast time
    let futureTime = dt + (60 * 60000)
    futureTime = futureTime.toLocaleString(DateTime.DATETIME_MED);

    // TODO finish this HTML
    return (
        <div className="selected-view">
            <div className="date-container">
                <h2 className="date-dayname">{currentTime}</h2>
                <span>
                    <HiOutlineLocationMarker color="white" className="location-icon" />
                </span>
                <span className="location">Amazon Park - Eugene, OR</span>
            </div>
            <div className="data-container">
                <h1 className="aqi">US AQI: {currentData}</h1>
                <h3 className="aqi-desc">{}</h3>
            </div>
        </div>
    )

}