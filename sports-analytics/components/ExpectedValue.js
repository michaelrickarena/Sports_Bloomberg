// ExpectedValue.js
"use client";

import { useEffect, useState, useMemo } from "react";
import "../styles/expectedvalue.css"; // Import the regular stylesheet

// Helper to format prop type strings
const formatPropType = (propType) => {
  if (!propType) return "";
  return propType
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

// Helper to format sport type strings
const formatSportType = (sportType) => {
  if (!sportType) return "";
  const formattedSportType = sportType.split("_").slice(1).join("_");
  return formattedSportType.toUpperCase();
};

export default function ExpectedValue() {
  const [moneylineData, setMoneylineData] = useState([]);
  const [propsData, setPropsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Sorting state for moneyline table
  const [moneylineSortConfig, setMoneylineSortConfig] = useState({
    key: null,
    direction: "asc",
  });
  // Sorting state for props table
  const [propsSortConfig, setPropsSortConfig] = useState({
    key: null,
    direction: "asc",
  });

  // Filter states for props table
  const [selectedBookie, setSelectedBookie] = useState("");
  const [minBookies, setMinBookies] = useState("");
  const [minFairProbability, setMinFairProbability] = useState("");
  const [lineOperator, setLineOperator] = useState("");
  const [lineValue, setLineValue] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (!sessionStorage.getItem("reloaded")) {
          sessionStorage.setItem("reloaded", "true");
          window.location.reload();
        }
        const [moneylineRes, propsRes] = await Promise.all([
          fetch(
            `${process.env.NEXT_PUBLIC_API_BASE_URL}/expected-value-moneyline/`
          ),
          fetch(
            `${process.env.NEXT_PUBLIC_API_BASE_URL}/expected-value-props/`
          ),
        ]);

        if (!moneylineRes.ok || !propsRes.ok) {
          throw new Error("Failed to fetch one or more endpoints");
        }

        const moneylineJson = await moneylineRes.json();
        const propsJson = await propsRes.json();

        setMoneylineData(moneylineJson);
        setPropsData(propsJson);
      } catch (err) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Compute unique bookies for the dropdown filter
  const uniqueBookies = useMemo(() => {
    const bookies = propsData.map((row) => row.Bookie);
    return [...new Set(bookies)].sort();
  }, [propsData]);

  // Filter props data based on user inputs
  const filteredPropsData = useMemo(() => {
    return propsData.filter((row) => {
      if (selectedBookie && row.Bookie !== selectedBookie) return false;
      if (minBookies !== "" && row.Num_Bookies <= Number(minBookies))
        return false;
      if (
        minFairProbability !== "" &&
        row.Fair_Probability <= Number(minFairProbability) / 100
      )
        return false;
      if (lineOperator && lineValue !== "") {
        const lineVal = Number(lineValue);
        if (lineOperator === ">" && row.Betting_Line <= lineVal) return false;
        if (lineOperator === "<" && row.Betting_Line >= lineVal) return false;
      }
      return true;
    });
  }, [
    propsData,
    selectedBookie,
    minBookies,
    minFairProbability,
    lineOperator,
    lineValue,
  ]);

  // Sorting functions for moneyline
  const handleMoneylineSort = (key) => {
    let direction = "asc";
    if (
      moneylineSortConfig.key === key &&
      moneylineSortConfig.direction === "asc"
    ) {
      direction = "desc";
    }
    setMoneylineSortConfig({ key, direction });
  };

  // Sorting functions for props
  const handlePropsSort = (key) => {
    let direction = "asc";
    if (propsSortConfig.key === key && propsSortConfig.direction === "asc") {
      direction = "desc";
    }
    setPropsSortConfig({ key, direction });
  };

  // Sorted moneyline data
  const sortedMoneylineData = useMemo(() => {
    let sortableItems = [...moneylineData];
    if (moneylineSortConfig.key !== null) {
      sortableItems.sort((a, b) => {
        let aVal = a[moneylineSortConfig.key];
        let bVal = b[moneylineSortConfig.key];
        if (!isNaN(aVal) && !isNaN(bVal)) {
          aVal = Number(aVal);
          bVal = Number(bVal);
        }
        if (aVal < bVal) {
          return moneylineSortConfig.direction === "asc" ? -1 : 1;
        }
        if (aVal > bVal) {
          return moneylineSortConfig.direction === "asc" ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableItems;
  }, [moneylineData, moneylineSortConfig]);

  // Sorted props data (uses filtered data)
  const sortedPropsData = useMemo(() => {
    let sortableItems = [...filteredPropsData];
    if (propsSortConfig.key !== null) {
      sortableItems.sort((a, b) => {
        let aVal = a[propsSortConfig.key];
        let bVal = b[propsSortConfig.key];
        if (!isNaN(aVal) && !isNaN(bVal)) {
          aVal = Number(aVal);
          bVal = Number(bVal);
        }
        if (aVal < bVal) {
          return propsSortConfig.direction === "asc" ? -1 : 1;
        }
        if (aVal > bVal) {
          return propsSortConfig.direction === "asc" ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableItems;
  }, [filteredPropsData, propsSortConfig]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="expectedvalue-sports">
      <h1 className="expectedvalue-sports-title">Current +EV Moneyline</h1>
      <div className="table-container">
        <table border="1" cellPadding="5">
          <thead>
            <tr>
              <th>Team</th>
              <th>Bookie</th>
              <th
                onClick={() => handleMoneylineSort("line")}
                style={{ cursor: "pointer" }}
              >
                Line{" "}
                {moneylineSortConfig.key === "line"
                  ? moneylineSortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleMoneylineSort("expected_value")}
                style={{ cursor: "pointer" }}
              >
                Expected Value{" "}
                {moneylineSortConfig.key === "expected_value"
                  ? moneylineSortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleMoneylineSort("fair_probability")}
                style={{ cursor: "pointer" }}
              >
                Fair Probability{" "}
                {moneylineSortConfig.key === "fair_probability"
                  ? moneylineSortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleMoneylineSort("implied_probability")}
                style={{ cursor: "pointer" }}
              >
                Implied Probability{" "}
                {moneylineSortConfig.key === "implied_probability"
                  ? moneylineSortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th>Market Overround</th>
              <th>Sport</th>
              <th>Event Timestamp</th>
              <th>Last Update</th>
            </tr>
          </thead>
          <tbody>
            {sortedMoneylineData.map((row) => (
              <tr key={row.id}>
                <td>{row.team}</td>
                <td>{row.bookie}</td>
                <td>{row.line}</td>
                <td>{row.expected_value}</td>
                <td>{(row.fair_probability * 100).toFixed(2)}%</td>
                <td>{(row.implied_probability * 100).toFixed(2)}%</td>
                <td>{row.market_overround}</td>
                <td>{formatSportType(row.sport_type)}</td>
                <td>{new Date(row.event_timestamp).toLocaleString()}</td>
                <td>{new Date(row.last_updated_timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h1 className="expectedvalue-sports-title">Current +EV Props</h1>
      <h4 className="expectedvalue-sports-content">+EV Prop Filters</h4>
      <div className="filter-container">
        <div className="filters">
          <div className="filter-item">
            <label htmlFor="bookie-select">Bookie:</label>
            <select
              id="bookie-select"
              value={selectedBookie}
              onChange={(e) => setSelectedBookie(e.target.value)}
            >
              <option value="">All</option>
              {uniqueBookies.map((bookie) => (
                <option key={bookie} value={bookie}>
                  {bookie}
                </option>
              ))}
            </select>
          </div>
          <div className="filter-item">
            <label htmlFor="min-bookies">Min # of Bookies:</label>
            <input
              id="min-bookies"
              type="number"
              value={minBookies}
              onChange={(e) => setMinBookies(e.target.value)}
              placeholder="e.g., 2"
            />
          </div>
          <div className="filter-item">
            <label htmlFor="min-fair-prob">Min Fair Probability (%):</label>
            <input
              id="min-fair-prob"
              type="number"
              value={minFairProbability}
              onChange={(e) => setMinFairProbability(e.target.value)}
              placeholder="e.g., 50"
            />
          </div>
          <div className="filter-item">
            <label>Line Filter:</label>
            <select
              value={lineOperator}
              onChange={(e) => setLineOperator(e.target.value)}
            >
              <option value="">None</option>
              <option value=">">Greater than</option>
              <option value="<">Less than</option>
            </select>
            <input
              type="number"
              value={lineValue}
              onChange={(e) => setLineValue(e.target.value)}
              placeholder="e.g., 100"
            />
          </div>
        </div>
      </div>
      <div className="table-container">
        <table border="1" cellPadding="5">
          <thead>
            <tr>
              <th>Player Name</th>
              <th>Bookie</th>
              <th>Prop Type</th>
              <th>Type</th>
              <th
                onClick={() => handlePropsSort("Betting_Line")}
                style={{ cursor: "pointer" }}
              >
                Line{" "}
                {propsSortConfig.key === "Betting_Line"
                  ? propsSortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th>O/U Line</th>
              <th
                onClick={() => handlePropsSort("Expected_Value")}
                style={{ cursor: "pointer" }}
              >
                Expected Value{" "}
                {propsSortConfig.key === "Expected_Value"
                  ? propsSortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handlePropsSort("Fair_Probability")}
                style={{ cursor: "pointer" }}
              >
                Fair Probability{" "}
                {propsSortConfig.key === "Fair_Probability"
                  ? propsSortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handlePropsSort("Implied_Probability")}
                style={{ cursor: "pointer" }}
              >
                Implied Probability{" "}
                {propsSortConfig.key === "Implied_Probability"
                  ? propsSortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th># of Bookies</th>
              <th>Sport</th>
              <th>Last Update</th>
            </tr>
          </thead>
          <tbody>
            {sortedPropsData.map((row) => (
              <tr key={row.id}>
                <td>{row.Player_Name}</td>
                <td>{row.Bookie}</td>
                <td>{formatPropType(row.Prop_Type)}</td>
                <td>{row.Bet_Type}</td>
                <td>{row.Betting_Line}</td>
                <td>{row.Betting_Point}</td>
                <td>{row.Expected_Value}</td>
                <td>{(row.Fair_Probability * 100).toFixed(2)}%</td>
                <td>{(row.Implied_Probability * 100).toFixed(2)}%</td>
                <td>{row.Num_Bookies}</td>
                <td>{formatSportType(row.sport_type)}</td>
                <td>{new Date(row.last_updated_timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
