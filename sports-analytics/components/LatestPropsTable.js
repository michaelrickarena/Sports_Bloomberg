import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import "../styles/LatestMoneylineTable.css"; // Use the same styling
import { formatTitle } from "../utils/utils.js";

const LatestPropsTable = ({ playerName, propType }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortConfig, setSortConfig] = useState({
    key: "betting_line", // Default column to sort
    direction: "ascending", // Default sort direction
  });

  useEffect(() => {
    if (!playerName || !propType) {
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const url = `${
          process.env.NEXT_PUBLIC_API_BASE_URL
        }/latest_props/?player_name=${encodeURIComponent(
          playerName
        )}&prop_type=${encodeURIComponent(propType)}`;

        const response = await fetch(url);

        if (!response.ok) {
          throw new Error(`Failed to fetch data. Status: ${response.status}`);
        }

        const result = await response.json();

        // Check if the data is an array or wrapped in a 'results' key
        if (Array.isArray(result)) {
          setData(result);
        } else if (result.results && Array.isArray(result.results)) {
          setData(result.results);
        } else {
          setData([]); // In case of an unexpected structure
        }
      } catch (err) {
        setError("Failed to load data.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [playerName, propType]);

  const sortData = (key) => {
    let direction = "ascending";
    if (sortConfig.key === key && sortConfig.direction === "ascending") {
      direction = "descending";
    }

    const sortedData = [...data].sort((a, b) => {
      if (key === "betting_line" || key === "betting_point") {
        return direction === "ascending" ? a[key] - b[key] : b[key] - a[key];
      }
      return 0; // Default case, if the column isn't one of those two
    });

    setData(sortedData);
    setSortConfig({ key, direction });
  };

  if (loading) {
    return <div>Loading data...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="table-container">
      <h3>{formatTitle(`Latest Odds: ${playerName} - ${propType}`)}</h3>

      <table className="latest-moneyline-table">
        <thead>
          <tr>
            <th>Bookie</th>
            <th>Bet Type</th>
            <th
              onClick={() => sortData("betting_line")}
              style={{ cursor: "pointer" }}
            >
              Betting Line{" "}
              {sortConfig.key === "betting_line"
                ? sortConfig.direction === "ascending"
                  ? "↑"
                  : "↓"
                : ""}
            </th>
            <th
              onClick={() => sortData("betting_point")}
              style={{ cursor: "pointer" }}
            >
              Betting Point{" "}
              {sortConfig.key === "betting_point"
                ? sortConfig.direction === "ascending"
                  ? "↑"
                  : "↓"
                : ""}
            </th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index}>
              <td>{item.bookie}</td>
              <td>{item.bet_type}</td>
              <td>{item.betting_line}</td>
              <td>{item.betting_point}</td>
              <td>{new Date(item.last_updated_timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

LatestPropsTable.propTypes = {
  playerName: PropTypes.string.isRequired,
  propType: PropTypes.string.isRequired,
};

export default LatestPropsTable;
