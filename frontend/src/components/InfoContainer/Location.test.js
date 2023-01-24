import renderer from "react-test-renderer";
import { render, screen } from "@testing-library/react";
import { useEffect, useState, useContext } from "react";
import TestAQIProvider from "../Fixtures";
import { Location } from "./Location";

// Set up Location with mock data
const Fixture = () => {
    const Child = () => {
        return(
            <Location />
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

describe("<Location />", () => {
    test("Create location container", () => {
        matches(<Fixture />);
    })
})

//TODO: add tests for handleChange


