import renderer from "react-test-renderer";
import { render, screen } from "@testing-library/react";
import { useEffect, useState, useContext } from "react";
import { AQIContext } from "../../contexts/AirQualityContext";
import TestAQIProvider from "../Fixtures";
import { SelectedView } from "./SelectedView";

// Set up Location with mock data
const Fixture = () => {
    const Child = () => {
        return(
            <SelectedView />
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

describe("<Selected View />", () => {
    test("Create element for viewing selected forecast time step", () => {
        matches(<Fixture />);
    })
})

