import renderer from "react-test-renderer";
import { render, screen } from "@testing-library/react";
import { useEffect, useState, useContext } from "react";
import { DayCard } from "./DayCard";
import { AQIContext, useAQIContext } from "../../contexts/AirQualityContext";
import TestAQIProvider from "../Fixtures.js";

// Set up DayCard with mock data
const Fixture = () => {
    const Child = () => {
        const { forecastData, futureTimeSteps, setCurrentData, setCurrentTime } = useAQIContext();
        const [selectedCard, setSelectedCard] = useState(0);
        const index = 3;
        const item = forecastData[index];
        return(
            <DayCard
                className={index === selectedCard ? "active" : ""}
                onClick={() => {
                    setSelectedCard(index);
                    setCurrentData(item);
                    setCurrentTime(futureTimeSteps[index]);
                }}
                key={index}
                index={index}
                item={item}
            />
        )
    };
    // Return DayCard wrapped within Provider
    return (
        <TestAQIProvider>
            <Child />
        </TestAQIProvider>
    );
}

// Helper function for snapshot testing
const matches = (children) => expect(
    renderer.create(children).toJSON()
).toMatchSnapshot();

// Tests
describe("<DayCard />", () => {

    test("Create day card element with current data", () => {
        matches(<Fixture />);
    });
})

