import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import "../styles/LatestMoneylineTable.css";
import { formatTitle } from "../utils/utils.js";

const LatestPropsTable = ({
  playerName,
  propType,
  selectedBetType,
  isOverUnderProp,
}) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortConfig, setSortConfig] = useState({
    key: "betting_line",
    direction: "ascending",
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

        let fetchedData = Array.isArray(result) ? result : result.results || [];

        // Filter data for over/under props based on selectedBetType, if set
        if (isOverUnderProp && selectedBetType) {
          fetchedData = fetchedData.filter(
            (item) => item.bet_type === selectedBetType
          );
        }

        setData(fetchedData);
      } catch (err) {
        setError("Failed to load data.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [playerName, propType, selectedBetType, isOverUnderProp]);

  const sortData = (key) => {
    let direction = "ascending";
    if (sortConfig.key === key && sortConfig.direction === "ascending") {
      direction = "descending";
    }

    const sortedData = [...data].sort((a, b) => {
      if (key === "betting_line" || key === "betting_point") {
        return direction === "ascending" ? a[key] - b[key] : b[key] - a[key];
      }
      return 0;
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

  // For over/under props, don't render until selectedBetType is set
  if (isOverUnderProp && !selectedBetType) {
    return <div>Please select Over or Under to view the table.</div>;
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
  selectedBetType: PropTypes.string, // Optional, can be null
  isOverUnderProp: PropTypes.bool, // Optional, can be false
};

export default LatestPropsTable;
