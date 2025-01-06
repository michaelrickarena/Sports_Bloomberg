"use client";

import React, { useState, useEffect } from "react";
import "../styles/LatestMoneylineTable.css"; // Import the CSS file

const LatestMoneylineTable = ({ gameId }) => {
  const [latestMoneylineData, setLatestMoneylineData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sortOrderHome, setSortOrderHome] = useState("ASC"); // Track sort order for home team
  const [sortOrderAway, setSortOrderAway] = useState("ASC"); // Track sort order for away team

  useEffect(() => {
    const fetchLatestMoneyline = async () => {
      if (!gameId) return;

      setLoading(true);
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/api/latest_moneyline/?game_id=${gameId}`
        );
        const data = await response.json();
        setLatestMoneylineData(data.results || []);
      } catch (error) {
        console.error("Error fetching latest moneyline data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchLatestMoneyline();
  }, [gameId]);

  if (!gameId) {
    return <p>Please select a game to view moneyline data.</p>;
  }

  // Home team data and sorting logic
  const homeTeamData = latestMoneylineData.map((row) => ({
    bookie: row.bookie,
    team: row.home_team,
    line: row.line_1,
    lastUpdated: row.last_updated_timestamp,
  }));

  const sortedHomeTeamData =
    sortOrderHome === "ASC"
      ? homeTeamData.sort((a, b) => a.line - b.line) // Sort ascending by line_1
      : homeTeamData.sort((a, b) => b.line - a.line); // Sort descending by line_1

  // Away team data and sorting logic
  const awayTeamData = latestMoneylineData.map((row) => ({
    bookie: row.bookie,
    team: row.away_team,
    line: row.line_2,
    lastUpdated: row.last_updated_timestamp,
  }));

  const sortedAwayTeamData =
    sortOrderAway === "ASC"
      ? awayTeamData.sort((a, b) => a.line - b.line) // Sort ascending by line_2
      : awayTeamData.sort((a, b) => b.line - a.line); // Sort descending by line_2

  // Toggle sorting for Home Team table
  const toggleSortHome = () => {
    setSortOrderHome(sortOrderHome === "ASC" ? "DESC" : "ASC");
  };

  // Toggle sorting for Away Team table
  const toggleSortAway = () => {
    setSortOrderAway(sortOrderAway === "ASC" ? "DESC" : "ASC");
  };

  return (
    <div>
      {loading ? (
        <p>Loading latest moneyline data...</p>
      ) : (
        <div className="table-container">
          {/* Home Team Table */}
          <div className="table-item">
            <h3>Most Recent Bookie Odds - Home Team</h3>
            <table>
              <thead>
                <tr>
                  <th>Bookie</th>
                  <th>Home Team</th>
                  <th onClick={toggleSortHome}>
                    Home Team Line {sortOrderHome === "ASC" ? "↑" : "↓"}
                  </th>
                  <th>Last Updated</th>
                </tr>
              </thead>
              <tbody>
                {sortedHomeTeamData.map((row, index) => (
                  <tr key={index}>
                    <td>{row.bookie}</td>
                    <td>{row.team}</td>
                    <td>{row.line}</td>
                    <td>{new Date(row.lastUpdated).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Away Team Table */}
          <div className="table-item">
            <h3>Most Recent Bookie Odds - Away Team</h3>
            <table>
              <thead>
                <tr>
                  <th>Bookie</th>
                  <th>Away Team</th>
                  <th onClick={toggleSortAway}>
                    Away Team Line {sortOrderAway === "ASC" ? "↑" : "↓"}
                  </th>
                  <th>Last Updated</th>
                </tr>
              </thead>
              <tbody>
                {sortedAwayTeamData.map((row, index) => (
                  <tr key={index}>
                    <td>{row.bookie}</td>
                    <td>{row.team}</td>
                    <td>{row.line}</td>
                    <td>{new Date(row.lastUpdated).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default LatestMoneylineTable;
