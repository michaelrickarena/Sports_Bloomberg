"use client";

import React, { useState, useEffect, useRef } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import {
  getColorForBookieProp,
  formatTimestamp,
  generateChartOptions,
} from "../utils/utils.js";
import { ClipLoader } from "react-spinners";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const PropDataGraph = ({
  selectedPlayer,
  selectedProp,
  bet_type,
  bet_type_name,
  selectedBookies,
  updateBookies,
  selectedBetType,
}) => {
  const [propData, setPropData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [bettingPoints, setBettingPoints] = useState([]);
  const [selectedBettingPoint, setSelectedBettingPoint] = useState("");
  const chartRef = useRef(null);

  const toggleBookieSelection = (bookie) => {
    updateBookies((prevSelected) => {
      if (prevSelected.includes(bookie)) {
        return prevSelected.filter((b) => b !== bookie);
      }
      return [...prevSelected, bookie];
    });
  };

  useEffect(() => {
    if (!selectedPlayer || !selectedProp) {
      return;
    }

    const fetchPropData = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/props/?player_name=${selectedPlayer}&prop_type=${selectedProp}`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch prop data");
        }

        const data = await response.json();

        if (!bet_type) {
          setPropData([]);
          setBettingPoints([]);
          setSelectedBettingPoint("");
          return;
        }

        let filteredData = data.results || [];

        // Filter data based on selectedBetType only if it’s not null
        if (selectedBetType !== null) {
          filteredData = filteredData.filter(
            (item) => item.bet_type === selectedBetType
          );
        }

        // Extract unique betting points
        const uniquePoints = [
          ...new Set(filteredData.map((item) => item.betting_point)),
        ];
        setBettingPoints(uniquePoints);
        setSelectedBettingPoint(uniquePoints[0] || "");

        setPropData(filteredData);
        const uniqueBookies = [
          ...new Set(filteredData.map((item) => item.bookie)),
        ];
        updateBookies(uniqueBookies);
      } catch (error) {
        console.error("Error fetching prop data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPropData();
  }, [selectedPlayer, selectedProp, bet_type, selectedBetType, updateBookies]);

  // Filter propData by selectedBettingPoint
  const filteredPropData = selectedBettingPoint
    ? propData.filter((item) => item.betting_point === selectedBettingPoint)
    : propData;

  if (loading) {
    return (
      <div style={{ textAlign: "center", marginTop: "20px" }}>
        <ClipLoader size={100} color="#007bff" />
        <p>Loading prop data... This may take a moment.</p>
      </div>
    );
  }

  if (filteredPropData.length === 0) {
    return <div>No valid data for this prop and bet type.</div>;
  }

  const allTimestamps = [
    ...new Set(filteredPropData.map((item) => item.last_updated_timestamp)),
  ];
  const sortedTimestamps = allTimestamps.sort();

  const bookieData = {};
  filteredPropData.forEach((item) => {
    const { bookie, last_updated_timestamp } = item;
    const betTypeValue = item[bet_type];

    if (!bookieData[bookie]) {
      bookieData[bookie] = { data: [] };
    }

    const timestampIndex = sortedTimestamps.indexOf(last_updated_timestamp);
    if (timestampIndex !== -1) {
      bookieData[bookie].data[timestampIndex] = betTypeValue;
    }
  });

  const chartData = {
    labels: sortedTimestamps.map((timestamp) => formatTimestamp(timestamp)),
    datasets: Object.keys(bookieData)
      .filter((bookie) => selectedBookies.includes(bookie))
      .map((bookie) => {
        const color = getColorForBookieProp(bookie.trim());
        const data = sortedTimestamps.map(
          (timestamp) =>
            bookieData[bookie].data[sortedTimestamps.indexOf(timestamp)] || null
        );
        return {
          label: bookie,
          data: data,
          borderColor: color,
          backgroundColor: color,
          tension: 0.1,
          borderWidth: 2,
          spanGaps: true,
        };
      }),
  };

  const isDataValid =
    chartData.datasets.length > 0 &&
    chartData.datasets.some((dataset) =>
      dataset.data.some(
        (value) => value !== null && value !== "N/A" && !isNaN(value)
      )
    );

  if (chartData.datasets.length === 0 || !isDataValid) {
    return <div>No Valid Data to Graph for {bet_type_name}</div>;
  }

  return (
    <div>
      <h4>
        {bet_type_name} for {selectedPlayer} -{" "}
        {selectedProp
          .replace(/_/g, " ")
          .replace(/\b\w/g, (char) => char.toUpperCase())}
      </h4>

      {/* Betting Point Dropdown */}
      {bettingPoints.length > 0 && (
        <div className="mb-4 flex items-center gap-2">
          <label
            htmlFor="betting-point-dropdown"
            className="text-sm font-semibold text-gray-700 mr-2"
          >
            Select Betting Point:
          </label>
          <select
            id="betting-point-dropdown"
            value={selectedBettingPoint}
            onChange={(e) => setSelectedBettingPoint(e.target.value)}
            className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200"
          >
            {bettingPoints.map((point) => (
              <option key={point} value={point}>
                {point}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="chart-wrapper">
        <Line
          ref={chartRef}
          data={chartData}
          options={generateChartOptions(chartData)}
        />
      </div>
    </div>
  );
};

export default PropDataGraph;
