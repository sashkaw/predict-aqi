import { useEffect, useState } from "react";
import { useAQIContext } from "../../contexts/AirQualityContext";
import { DayCard } from "../DayCard";

export function TimeStepsInfo() {
    const { forecastData, setCurrentData } = useAQIContext();
    const [selectedCard, setSelectedCard] = useState(0);

    useEffect(() => {
        setCurrentData(forecastData[selectedCard]);
    }, [forecastData]); // Skip effect if current data already set

    return (
        <div className="timesteps-container">
            <ul className="timesteps-list">
                {forecastData.map((item, index) => {
                    if(index < 12) { //TODO: change this to fit number of timesteps dynamically
                        return (
                            <DayCard
                                className={index === selectedCard ? "active": ""}
                                onClick={() => {
                                    setSelectedCard(index);
                                    setCurrentData(item);
                                }}
                                key={index}
                                item={item}
                            />
                        );
                    } 
                })}
                <div className="clear"></div>
            </ul>
        </div>
    );
}


/*const aqi_level = (aqi) => {
    const level = {};
    if(aqi >= 0 && aqi <= 50) {
        level = {
            "good: green",
        };
    }
    else if(aqi <= 100) {
        level = {
            "moderate: yellow",
        };
    }
    else if(aqi <= 150) {
        level = {
            "unhealthy for sensitive groups": "orange",
        }
    }
    else if(aqi <= 200) {
        level = {
            "unhealthy": "red",
        }
    }
    else if(aqi <= 300) {
        level = {
            "very unhealthy": "purple",
        }
    }
    else if(aqi <= 500) {
        level = {
            "hazardous": "maroon",
        }
    }

    return level;
}*/