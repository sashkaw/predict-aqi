import renderer from "react-test-renderer";
import { render, screen } from "@testing-library/react";
import { useEffect, useState, useContext } from "react";
import TestAQIProvider from "../Fixtures";
import { TimeStepsInfo } from "./TimeStepsInfo";
import { Location } from "./Location";
import { InfoContainer } from "./InfoContainer";

// Set up DayCard with mock data
const Fixture = () => {
    const Child = () => {
        return(
            <TimeStepsInfo />
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

describe("<InfoContainer />", () => {
    test("Creates container for forecast time steps", () => {
        matches(<Fixture />);

    })
})