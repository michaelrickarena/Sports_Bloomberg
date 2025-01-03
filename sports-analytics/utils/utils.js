// utils.js
export const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  const formattedDate = `${date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
  })}, ${date.getHours() % 12 === 0 ? 12 : date.getHours() % 12}${
    date.getMinutes() === 0 ? "" : ""
  } ${date.getHours() < 12 ? "AM" : "PM"}`;
  return formattedDate;
};

export const getColorForBookie = (bookie) => {
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

export const groupGamesByDate = (games) => {
  return games.reduce((acc, game) => {
    // Ensure event_timestamp is defined and valid
    if (
      !game.event_timestamp ||
      isNaN(new Date(game.event_timestamp).getTime())
    ) {
      console.error("Invalid timestamp:", game.event_timestamp); // Log invalid timestamp
      return acc; // Skip this game if the timestamp is invalid
    }

    // Convert event_timestamp to a Date object
    const date = new Date(game.event_timestamp);

    // Format the date as "2024/12/25"
    const formattedDate = date.toLocaleDateString("en-CA"); // 'en-CA' is the format for YYYY/MM/DD

    if (!acc[formattedDate]) {
      acc[formattedDate] = [];
    }
    acc[formattedDate].push(game);
    return acc;
  }, {});
};

// generateChartData

export const generateBaseChartData = (
  data,
  timestamps,
  selectedBookies,
  formatTimestamp,
  getColorForBookie,
  teamKey
) => {
  const bookieDataMap = {};

  data.forEach((entry) => {
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
      bookieDataMap[entry.bookie].data[timestampIndex] = entry[teamKey]; // This is where line_1 or line_2 will go
    }
  });

  const filteredDatasets = Object.values(bookieDataMap).filter((item) =>
    selectedBookies.includes(item.label)
  );

  return {
    datasets: filteredDatasets,
    labels: timestamps,
  };
};

export const generateChartOptions = () => {
  return {
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
  };
};
