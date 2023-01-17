import { TimeStepsInfo } from "./TimeStepsInfo";
import { Location } from "./Location";

export function InfoContainer() {
    return (
        <div className="info-container">
            <TimeStepsInfo />
            <Location />
        </div>
    );
}