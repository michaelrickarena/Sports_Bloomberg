"use client";

import React, { useState, useEffect } from "react";
import { ClipLoader } from "react-spinners";
import { Line } from "react-chartjs-2";
import LatestMoneylineTable from "./LatestMoneylineTable";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip
);
import Chart from "chart.js/auto";
import {
  formatTimestamp,
  getColorForBookie,
  groupGamesByDate,
  generateBaseChartData,
  generateChartOptions,
} from "../utils/utils.js";

const DropdownWithCharts = ({ sportTitle }) => {
  const [games, setGames] = useState([]);
  const [groupedGames, setGroupedGames] = useState({});
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
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/upcoming_games/?sport_title=${sportTitle}`
        );
        const data = await response.json();
        setGames(data);
        setGroupedGames(groupGamesByDate(data)); // Group the games here
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
  }, [abortController, sportTitle]);

  const handleGameSelect = async (event) => {
    const gameId = event.target.value;
    setSelectedGameId(gameId);

    if (gameId && gameId !== previousGameId) {
      setPreviousGameId(gameId); // Update the previous game ID
      setLoadingData(true); // Set loadingData to true when new data is being fetched

      try {
        const controller = new AbortController();
        setAbortController(controller);

        let nextUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/moneyline/?game_id=${gameId}`;
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

  const generateChartData = (teamKey) => {
    if (!moneylineData || moneylineData.length === 0) {
      return { labels: [], datasets: [] };
    }

    const sortedData = [...moneylineData].sort(
      (a, b) =>
        new Date(a.last_updated_timestamp) - new Date(b.last_updated_timestamp)
    );

    const timestamps = [];
    const { datasets } = generateBaseChartData(
      sortedData,
      timestamps,
      selectedBookies,
      formatTimestamp,
      getColorForBookie,
      teamKey
    );

    return {
      labels: timestamps,
      datasets: datasets,
    };
  };

  const chartData1 = generateChartData("line_1");
  const chartData2 = generateChartData("line_2");
  const chartOptions1 = generateChartOptions(chartData1);
  const chartOptions2 = generateChartOptions(chartData2);

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

  if (loading) {
    return (
      <div style={{ textAlign: "center", marginTop: "20px" }}>
        <ClipLoader size={100} color="#007bff" />
        <p>Loading games...</p>
      </div>
    );
  }

  if (!games.length) {
    return <p>No games available.</p>;
  }

  return (
    <div>
      <h2>Select a Game Below</h2>
      <select onChange={handleGameSelect} defaultValue="">
        <option value="" disabled>
          Select a game to view details
        </option>
        {Object.keys(groupedGames).map((date) => (
          <optgroup key={date} label={date}>
            {groupedGames[date].map((game) => (
              <option key={game.game_id} value={game.game_id}>
                {game.home_team} vs. {game.away_team}
              </option>
            ))}
          </optgroup>
        ))}
      </select>

      {/* Render loading message when data is being fetched */}
      {loadingData && (
        <div style={{ textAlign: "center", marginTop: "20px" }}>
          <ClipLoader size={100} color="#007bff" />
          <p>Loading data... This may take 30 seconds</p>
        </div>
      )}

      {/* Render the LatestMoneylineTable component */}
      <LatestMoneylineTable
        gameId={selectedGameId}
        endpoint="latest_moneyline"
        line1="line_1"
        line2="line_2"
        home_team="home_team"
        away_team="away_team"
      />

      {!loadingData && moneylineData.length > 0 && (
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
              <Line data={chartData1} options={chartOptions1} />
            </div>
            <div className="chart-container">
              <h4>Away Team: {moneylineData[0].away_team}</h4>
              <Line data={chartData2} options={chartOptions2} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DropdownWithCharts;
