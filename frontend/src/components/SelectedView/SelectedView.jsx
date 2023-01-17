import { useAQIContext } from "../../contexts/AirQualityContext";
import { HiOutlineLocationMarker } from "react-icons/hi";
import dayjs from "dayjs";

export function SelectedView() {
    // Get current AQI and forecast AQI
    const { site, currentData } = useAQIContext();

    // Show loading message if waiting for data
    if(!currentData) return <div>Loading...</div>

    // Get current time
    const currentTime = dayjs().format("MMM D, YYYY - h:m a");

    // TODO: Add function to map AQI's to string definitions
    return (
        <div className="selected-view">
            <div className="date-container">
                <h2 className="date-dayname">{currentTime}</h2>
                <span>
                    <HiOutlineLocationMarker color="white" className="location-icon" />
                </span>
                <span className="location">{site.name}</span>
            </div>
            <div className="aqi-container">
                <h1 className="aqi">AQI: {currentData}</h1>
            </div>
        </div>
    )

}