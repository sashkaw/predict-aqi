import React, { Component }from 'react';
import ReactDOM from 'react-dom/client';
import { InfoContainer } from "./InfoContainer";
import { SelectedView } from "./SelectedView";
import { AQIProvider } from '../contexts/AirQualityContext';

export default class App extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <AQIProvider>
                <div className="wrapper">
                    <div className="container">
                        <SelectedView />
                        <InfoContainer />
                    </div>
                </div>
            </AQIProvider>
        );
    }
}

const appDiv = document.getElementById('app');
const root = ReactDOM.createRoot(appDiv);
root.render(<App />);