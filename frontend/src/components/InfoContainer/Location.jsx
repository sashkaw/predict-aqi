import { useAQIContext } from "../../contexts/AirQualityContext";
import sites from "../../monitoring_sites.json";

export function Location() {
    const { setSite } = useAQIContext();

    function handleChange(event) {
        const selectedSite = sites.filter(
            (site) => site.id == Number(event.target.value)
        )[0];
        setSite(selectedSite);
    }

    return (
        <div className="location-container">
            <select 
                defaultValue={"1"}
                onChange={handleChange}
                className="location-button"
            >
                {sites.map((site) => {
                    return (
                        <option value={site.id} key={site.id}>
                            {site.name}
                        </option>
                    );
                })}
            </select>
        </div>
    );
}
