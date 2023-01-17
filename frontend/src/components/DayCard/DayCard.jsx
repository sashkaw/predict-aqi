import dayjs from "dayjs";
import { useAQIContext } from "../../contexts/AirQualityContext";

export function DayCard({ item, index, className, onClick }) {
    // Get current time step based on forecast data index
    const { futureTimeSteps } = useAQIContext();
    const cardTimeStep = futureTimeSteps[index];

    return (
        <li className={className} onClick={onClick}>
            <span className="timestep-name">{cardTimeStep}</span>
            <span className="timestep-aqi">{item}</span>
        </li>
    );
}