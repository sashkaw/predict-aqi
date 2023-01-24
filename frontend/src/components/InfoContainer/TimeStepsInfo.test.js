import renderer from "react-test-renderer";
import { render, screen } from "@testing-library/react";
import { useEffect, useState, useContext } from "react";
import { AQIContext } from "../../contexts/AirQualityContext";
import TestAQIProvider from "../Fixtures";
import { TimeStepsInfo } from "./TimeStepsInfo";

// Set up Location with mock data
const Fixture = () => {
    const Child = () => {
        return(
            <TimeStepsInfo />
        )
    };
    // Return Location wrapped within Provider
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

describe("<TimeStepsInfo />", () => {
    test("Create time step info elements", () => {
        matches(<Fixture />);
    })
})