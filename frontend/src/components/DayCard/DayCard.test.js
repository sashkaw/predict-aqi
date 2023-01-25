import renderer, { act } from "react-test-renderer";
import { getByRole, render, screen } from "@testing-library/react";
import { useEffect, useState, useContext } from "react";
import { DayCard } from "./DayCard";
import { AQIContext, useAQIContext } from "../../contexts/AirQualityContext";
import TestAQIProvider from "../Fixtures.js";
import { unmountComponentAtNode } from "react-dom";
import { toBeInTheDocument } from "@testing-library/jest-dom";

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
    let container = null;
    beforeEach(() => {
        // Setup a DOM element as a render target
        container = document.createElement("div");
        document.body.appendChild(container);
    });
    afterEach(() => {
        // Cleanup on exiting
        unmountComponentAtNode(container);
        container.remove();
        container = null;
    });

    test("Renders DayCard element and text content", () => {
        const { getByRole } = render(<Fixture />, container);
        // Renders list item
        expect(getByRole("listitem")).toBeInTheDocument();
        // Renders forecast timestep and data
        expect(document.body.querySelector(".timestep-name").textContent).toBe("2pm");
        expect(document.body.querySelector(".timestep-aqi").textContent).toBe("AQI: 5");
        // Render matches snapshot
        matches(<Fixture />);
    });
})

