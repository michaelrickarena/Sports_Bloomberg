"use client";

import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip
);

const DropdownWithCharts = () => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedGameId, setSelectedGameId] = useState(null);
  const [moneylineData, setMoneylineData] = useState([]);
  const [previousGameId, setPreviousGameId] = useState(null); // Store the previously selected game
  const [abortController, setAbortController] = useState(null); // Store the abort controller
  const [selectedBookies, setSelectedBookies] = useState([]); // Store selected bookies
  const [loadingData, setLoadingData] = useState(false); // Track if data is being loaded

  useEffect(() => {
    const fetchGames = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/upcoming_games/"
        );
        const data = await response.json();
        setGames(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching games:", error);
        setLoading(false);
      }
    };

    fetchGames();

    return () => {
      if (abortController) {
        abortController.abort(); // Cleanup on component unmount or game change
      }
    };
  }, [abortController]);

  const handleGameSelect = async (event) => {
    const gameId = event.target.value;
    setSelectedGameId(gameId);

    if (gameId && gameId !== previousGameId) {
      setPreviousGameId(gameId); // Update the previous game ID
      setLoadingData(true); // Set loadingData to true when new data is being fetched

      try {
        const controller = new AbortController();
        setAbortController(controller);

        let nextUrl = `http://127.0.0.1:8000/api/moneyline/?game_id=${gameId}`;
        let allMoneylineData = [];
        let abortFlag = false;

        // Fetch data with pagination
        while (nextUrl && !abortFlag) {
          const response = await fetch(nextUrl, {
            signal: controller.signal, // Pass the abort signal
          });

          if (!response.ok) {
            abortFlag = true; // Abort if response is not OK
            console.error("Request aborted or failed");
            break;
          }

          const data = await response.json();
          allMoneylineData = [...allMoneylineData, ...data.results];
          nextUrl = data.next;
        }

        setMoneylineData(allMoneylineData);

        // Set all bookies as selected initially
        const allBookies = allMoneylineData.map((item) => item.bookie);
        setSelectedBookies(allBookies);
      } catch (error) {
        console.error("Error fetching moneyline data:", error);
        setMoneylineData([]);
      } finally {
        setLoadingData(false); // Set loadingData to false once data is fetched
      }
    } else {
      setMoneylineData([]);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const formattedDate = `${date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
    })}, ${date.getHours() % 12 === 0 ? 12 : date.getHours() % 12}${
      date.getMinutes() === 0 ? "" : ""
    } ${date.getHours() < 12 ? "AM" : "PM"}`;
    return formattedDate;
  };

  const generateChartData = (teamKey) => {
    if (!moneylineData || moneylineData.length === 0) {
      return { labels: [], datasets: [] };
    }

    const sortedData = [...moneylineData].sort(
      (a, b) =>
        new Date(a.last_updated_timestamp) - new Date(b.last_updated_timestamp)
    );

    const timestamps = [];
    const bookieDataMap = {};

    sortedData.forEach((entry) => {
      const timestamp = formatTimestamp(entry.last_updated_timestamp);
      if (!timestamps.includes(timestamp)) {
        timestamps.push(timestamp);
      }

      if (!bookieDataMap[entry.bookie]) {
        bookieDataMap[entry.bookie] = {
          label: entry.bookie,
          data: new Array(timestamps.length).fill(null),
          borderColor: getColorForBookie(entry.bookie),
          backgroundColor: getColorForBookie(entry.bookie), // Set fill color
          fill: false,
          tension: 0.1,
          spanGaps: true,
          pointHoverBackgroundColor: getColorForBookie(entry.bookie), // Highlight color
          pointHoverBorderColor: getColorForBookie(entry.bookie),
        };
      }

      const timestampIndex = timestamps.indexOf(timestamp);
      if (timestampIndex !== -1) {
        bookieDataMap[entry.bookie].data[timestampIndex] = entry[teamKey];
      }
    });

    const filteredDatasets = Object.values(bookieDataMap).filter((item) =>
      selectedBookies.includes(item.label)
    );

    return {
      labels: timestamps,
      datasets: filteredDatasets,
      options: {
        responsive: true,
        plugins: {
          tooltip: {
            backgroundColor: (context) =>
              context.tooltipItems[0].dataset.borderColor, // Tooltip color matches line color
            callbacks: {
              title: (tooltipItem) => {
                const tooltipIndex = tooltipItem[0].dataIndex;
                const bookie = tooltipItem[0].dataset.label;
                const lineValue = tooltipItem[0].dataset.data[tooltipIndex];
                return `${bookie}: ${lineValue}`;
              },
            },
          },
        },
        hover: {
          mode: "nearest",
          intersect: false,
        },
        elements: {
          point: {
            hoverBackgroundColor: (context) => context.hoverColor, // Match point hover
          },
        },
      },
    };
  };

  const handleBookieSelect = (bookie) => {
    setSelectedBookies((prevSelected) => {
      if (prevSelected.includes(bookie)) {
        return prevSelected.filter((item) => item !== bookie); // Unselect bookie
      } else {
        return [...prevSelected, bookie]; // Select bookie
      }
    });
  };

  const uniqueBookies = [...new Set(moneylineData.map((item) => item.bookie))];

  const getColorForBookie = (bookie) => {
    const colors = {
      DraftKings: "#28a745",
      FanDuel: "#F33711",
      "MyBookie.ag": "#1e88e5",
      BetRivers: "#EB6BE8",
      Caesars: "#31DFF7",
      BetMGM: "#8B1388",
      "LowVig.ag": "#9A837E",
      "BetOnline.ag": "#FCFC5A",
      Bovada: "#000000",
      BetUS: "#FFA500",
    };

    return colors[bookie] || "#000000"; // Default to black if bookie color is not defined
  };

  if (loading) {
    return <p>Loading games...</p>;
  }

  if (!games.length) {
    return <p>No games available.</p>;
  }

  return (
    <div>
      <h2>Select a Game Below</h2>
      <select onChange={handleGameSelect}>
        <option value="">Select a game</option>
        {games.map((game) => (
          <option key={game.id} value={game.game_id}>
            {game.home_team} vs. {game.away_team}
          </option>
        ))}
      </select>

      {/* Render loading message when data is being fetched */}
      {loadingData && <p>Loading data... This may take 30 seconds</p>}

      {/* Render checkboxes for bookies above the charts */}
      {moneylineData.length > 0 && !loadingData && (
        <div>
          <h3>Line Movements</h3>
          {/* Select Bookies section */}
          <div>
            <h4>Select Bookies</h4>
            <div className="bookie-checkboxes">
              {uniqueBookies.map((bookie) => (
                <div key={bookie}>
                  <input
                    type="checkbox"
                    id={bookie}
                    checked={selectedBookies.includes(bookie)}
                    onChange={() => handleBookieSelect(bookie)}
                  />
                  <label htmlFor={bookie}>{bookie}</label>
                </div>
              ))}
            </div>
          </div>
          <div className="chart-wrapper">
            <div className="chart-container">
              <h4>Home Team: {moneylineData[0].home_team}</h4>
              <Line data={generateChartData("line_1")} />
            </div>
            <div className="chart-container">
              <h4>Away Team: {moneylineData[0].away_team}</h4>
              <Line data={generateChartData("line_2")} />
            </div>
          </div>
          {/* Bookie legend - moved below the charts */}
          <div
            className="bookie-legend"
            style={{
              marginTop: "20px",
              display: "flex",
              justifyContent: "center",
              flexDirection: "column",
              alignItems: "center",
            }}
          >
            <h4>Bookie Legend</h4>
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                justifyContent: "center",
              }}
            >
              {uniqueBookies.map((bookie) => (
                <div
                  key={bookie}
                  style={{
                    display: "flex", // Align items horizontally
                    alignItems: "center", // Vertically center the items
                    marginRight: "20px", // Space between each legend item
                    marginBottom: "10px", // Space between rows when wrapping
                  }}
                >
                  <span
                    style={{
                      display: "inline-block",
                      width: "20px",
                      height: "20px",
                      backgroundColor: getColorForBookie(bookie),
                      marginRight: "8px",
                    }}
                  ></span>
                  {bookie}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DropdownWithCharts;