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
import { getColorForBookieProp, formatTimestamp } from "../utils/utils.js";

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
}) => {
  const [propData, setPropData] = useState([]);
  const [loading, setLoading] = useState(false);
  const chartRef = useRef(null);

  const toggleBookieSelection = (bookie) => {
    updateBookies((prevSelected) => {
      console.log("Toggling bookie:", bookie);
      if (prevSelected.includes(bookie)) {
        return prevSelected.filter((b) => b !== bookie);
      }
      return [...prevSelected, bookie];
    });
  };

  useEffect(() => {
    console.log("useEffect triggered");
    console.log("selectedPlayer:", selectedPlayer);
    console.log("selectedProp:", selectedProp);
    console.log("bet_type:", bet_type);

    if (!selectedPlayer || !selectedProp) {
      console.log("No player or prop selected, skipping data fetch");
      return;
    }

    const fetchPropData = async () => {
      setLoading(true);
      try {
        console.log("Fetching prop data...");
        const response = await fetch(
          `http://127.0.0.1:8000/api/props/?player_name=${selectedPlayer}&prop_type=${selectedProp}`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch prop data");
        }

        const data = await response.json();

        if (!bet_type) {
          console.error("Error: bet_type is not defined!");
          return;
        }

        setPropData(data.results || []);
        const uniqueBookies = [
          ...new Set(data.results.map((item) => item.bookie)),
        ];
        updateBookies(uniqueBookies);
      } catch (error) {
        console.error("Error fetching prop data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPropData();
  }, [selectedPlayer, selectedProp, bet_type, updateBookies]);

  useEffect(() => {
    console.log("Component re-rendered");
  }, [propData, selectedBookies]);

  if (loading) {
    console.log("Loading prop data...");
    return <div>Loading prop data...</div>;
  }

  if (propData.length === 0) {
    console.log("No valid data for this prop.");
    return <div>No valid data for this prop.</div>;
  }

  const allTimestamps = [
    ...new Set(propData.map((item) => item.last_updated_timestamp)),
  ];
  const sortedTimestamps = allTimestamps.sort();

  const bookieData = {};
  propData.forEach((item) => {
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
    labels: sortedTimestamps.map((timestamp) => formatTimestamp(timestamp)), // Use formatTimestamp here
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
    console.log("No data to graph.");
    return <div>No Valid Data to Graph - This Prop Is Not An Over/Under.</div>;
  }

  return (
    <div>
      <h4>
        {bet_type_name} for {selectedPlayer} -{" "}
        {selectedProp
          .replace(/_/g, " ")
          .replace(/\b\w/g, (char) => char.toUpperCase())}
      </h4>

      <div className="chart-wrapper">
        <Line
          ref={chartRef}
          data={chartData}
          options={{
            maintainAspectRatio: false,
            animation: false, // Turn off animation for better performance
            tooltips: {
              enabled: false, // Disable tooltips on mobile for better performance
            },
            scales: {
              x: {
                display: window.innerWidth <= 768 ? false : true, // Hide x-axis on small screens
                ticks: {
                  callback: (val, index) =>
                    index % 5 === 0 ? chartData.labels[val] : "",
                },
              },
            },
            plugins: {
              legend: {
                display: window.innerWidth <= 768 ? false : true, // Hide the legend on small screens
              },
            },
          }}
        />
      </div>
    </div>
  );
};

export default PropDataGraph;
