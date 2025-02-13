import Chart from "chart.js/auto";

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
    "BetOnline.ag": "#DFDA03",
    Bovada: "#000000",
    BetUS: "#FFA500",
    Fanatics: "#ADFF5B",
  };

  return colors[bookie] || "#000000"; // Default to black if bookie color is not defined
};

export const getColorForBookieProp = (bookie) => {
  const colors = {
    DraftKings: "#28a745",
    FanDuel: "#F33711",
    "MyBookie.ag": "#1e88e5",
    BetRivers: "#EB6BE8",
    Caesars: "#31DFF7",
    BetMGM: "#8B1388",
    "LowVig.ag": "#9A837E",
    "BetOnline.ag": "#DFDA03",
    Bovada: "#000000",
    BetUS: "#FFA500",
    Fanatics: "#ADFF5B",
    WilliamHill: "#1B02AE",
  };

  // Bookie name mappings for props
  const bookieMappings = {
    fanduel: "FanDuel",
    draftkings: "DraftKings",
    betmgm: "BetMGM",
    williamhill_us: "WilliamHill", // Map specific variations
    betrivers: "BetRivers",
    bovada: "Bovada",
    betus: "BetUS",
    betonlineag: "BetOnline.ag", // Map lowercase to correct format
  };

  // Normalize the bookie name for color matching
  const normalizedBookie =
    bookieMappings[bookie.toLowerCase()] ||
    bookie.trim().replace(/\b\w/g, (char) => char.toUpperCase());

  return colors[normalizedBookie] || "#000000"; // Default to black if bookie color is not defined
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

  // Filter datasets based on selectedBookies
  const filteredDatasets = Object.values(bookieDataMap).filter((item) =>
    selectedBookies.includes(item.label)
  );

  return {
    datasets: filteredDatasets,
    labels: timestamps,
  };
};

export const generateChartOptions = (chartData) => {
  const isClient = typeof window !== "undefined"; // Check if running on the client side

  return {
    responsive: true,
    plugins: {
      legend: {
        display: isClient ? window.innerWidth > 1000 : true, // Default to true on the server
        position: "top",
        labels: {
          boxWidth: 20,
          padding: 15,
          font: {
            size: isClient ? (window.innerWidth <= 768 ? 10 : 12) : 12, // Default font size on the server
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
        hoverBackgroundColor: (context) => context.hoverColor,
      },
    },
    scales: {
      x: {
        ticks: {
          maxRotation: 0, // Force horizontal labels
          minRotation: 0, // Prevent any rotation
          autoSkip: true, // Automatically skip labels if they don’t fit
          maxTicksLimit: 5, // Limit the number of labels shown
          callback: (val, index) => {
            return isClient && window.innerWidth <= 1000 && index % 2 !== 0
              ? ""
              : chartData.labels[val];
          },
        },
      },
    },
  };
};

export const formatTitle = (title) => {
  return title
    .replace(/_/g, " ") // Replace underscores with spaces
    .split(" ") // Split by spaces
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()) // Capitalize each word
    .join(" "); // Join the words back into a string
};
