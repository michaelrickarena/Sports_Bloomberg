"use client";

import { useEffect, useState, useMemo } from "react";
import "../styles/expectedvalue.css";

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

export default function Arbitrage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: "asc" });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/arbitrage/`
        );
        if (!res.ok) {
          throw new Error("Failed to fetch arbitrage data");
        }
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSort = (key) => {
    let direction = "asc";
    if (sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc";
    }
    setSortConfig({ key, direction });
  };

  const sortedData = useMemo(() => {
    let sortableItems = [...data];
    if (sortConfig.key !== null) {
      sortableItems.sort((a, b) => {
        let aVal = a[sortConfig.key];
        let bVal = b[sortConfig.key];
        if (!isNaN(aVal) && !isNaN(bVal)) {
          aVal = Number(aVal);
          bVal = Number(bVal);
        }
        if (aVal < bVal) {
          return sortConfig.direction === "asc" ? -1 : 1;
        }
        if (aVal > bVal) {
          return sortConfig.direction === "asc" ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableItems;
  }, [data, sortConfig]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="expectedvalue-sports">
      <h1 className="expectedvalue-sports-title">Arbitrage Opportunities</h1>
      <div className="table-container">
        <table border="1" cellPadding="5">
          <thead>
            <tr>
              <th
                onClick={() => handleSort("Player_Name")}
                style={{ cursor: "pointer" }}
              >
                Player Name{" "}
                {sortConfig.key === "Player_Name"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleSort("Prop_Type")}
                style={{ cursor: "pointer" }}
              >
                Prop Type{" "}
                {sortConfig.key === "Prop_Type"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleSort("Betting_Point")}
                style={{ cursor: "pointer" }}
              >
                Betting Point{" "}
                {sortConfig.key === "Betting_Point"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleSort("sport_type")}
                style={{ cursor: "pointer" }}
              >
                Sport{" "}
                {sortConfig.key === "sport_type"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleSort("bookie_one")}
                style={{ cursor: "pointer" }}
              >
                Bookie One{" "}
                {sortConfig.key === "bookie_one"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleSort("outcome_one")}
                style={{ cursor: "pointer" }}
              >
                Outcome One{" "}
                {sortConfig.key === "outcome_one"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleSort("odds_one")}
                style={{ cursor: "pointer" }}
              >
                Odds One{" "}
                {sortConfig.key === "odds_one"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleSort("bet_amount_one")}
                style={{ cursor: "pointer" }}
              >
                Bet Amount One{" "}
                {sortConfig.key === "bet_amount_one"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleSort("bookie_two")}
                style={{ cursor: "pointer" }}
              >
                Bookie Two{" "}
                {sortConfig.key === "bookie_two"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleSort("outcome_two")}
                style={{ cursor: "pointer" }}
              >
                Outcome Two{" "}
                {sortConfig.key === "outcome_two"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleSort("odds_two")}
                style={{ cursor: "pointer" }}
              >
                Odds Two{" "}
                {sortConfig.key === "odds_two"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleSort("bet_amount_two")}
                style={{ cursor: "pointer" }}
              >
                Bet Amount Two{" "}
                {sortConfig.key === "bet_amount_two"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleSort("profit_percentage")}
                style={{ cursor: "pointer" }}
              >
                Profit Percentage{" "}
                {sortConfig.key === "profit_percentage"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
              <th
                onClick={() => handleSort("last_updated_timestamp")}
                style={{ cursor: "pointer" }}
              >
                Last Update{" "}
                {sortConfig.key === "last_updated_timestamp"
                  ? sortConfig.direction === "asc"
                    ? "▲"
                    : "▼"
                  : ""}
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row) => (
              <tr key={row.id}>
                <td>{row.Player_Name}</td>
                <td>{formatPropType(row.Prop_Type)}</td>
                <td>{row.Betting_Point}</td>
                <td>{formatSportType(row.sport_type)}</td>
                <td>{row.bookie_one}</td>
                <td>{row.outcome_one}</td>
                <td>{row.odds_one}</td>
                <td>{row.bet_amount_one.toFixed(2)}</td>
                <td>{row.bookie_two}</td>
                <td>{row.outcome_two}</td>
                <td>{row.odds_two}</td>
                <td>{row.bet_amount_two.toFixed(2)}</td>
                <td>{row.profit_percentage.toFixed(2)}%</td>
                <td>{new Date(row.last_updated_timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
