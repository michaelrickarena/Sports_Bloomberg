"use client";

import React, { useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";
import PropTypeDropdown from "./PropTypeDropdown";
import PropDataGraph from "./PropDataGraph";
import LatestPropsTable from "./LatestPropsTable";
import { ClipLoader } from "react-spinners";

const PlayerProps = ({ sportType }) => {
  const [playerNames, setPlayerNames] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState("");
  const [selectedProp, setSelectedProp] = useState("");
  const [uniqueBookies, setUniqueBookies] = useState([]);
  const [selectedBookies, setSelectedBookies] = useState([]);
  const [availableBetTypes, setAvailableBetTypes] = useState([]);
  const [selectedBetType, setSelectedBetType] = useState(null);
  const [betTypesLoading, setBetTypesLoading] = useState(false);

  useEffect(() => {
    const fetchPlayerNames = async () => {
      setLoading(true);
      setError(null);

      try {
        let allPlayerNames = [];
        let nextUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/distinct_props/?sport_type=${sportType}`;

        while (nextUrl) {
          const response = await fetch(nextUrl);
          if (!response.ok) {
            throw new Error("Failed to fetch data");
          }
          const data = await response.json();
          allPlayerNames = [
            ...allPlayerNames,
            ...data.results.map((player) => player.player_name),
          ];
          nextUrl = data.next;
        }

        const uniquePlayerNames = [...new Set(allPlayerNames)].sort();
        setPlayerNames(uniquePlayerNames);
      } catch (err) {
        setError("Failed to load player names.");
      } finally {
        setLoading(false);
      }
    };

    fetchPlayerNames();
  }, [sportType]);

  useEffect(() => {
    if (selectedPlayer && selectedProp) {
      const fetchAvailableBetTypes = async () => {
        setBetTypesLoading(true);
        try {
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_BASE_URL}/latest_props/?player_name=${selectedPlayer}&prop_type=${selectedProp}`
          );
          if (!response.ok) throw new Error("Failed to fetch latest props");
          const data = await response.json();
          const betTypes = [...new Set(data.map((item) => item.bet_type))];
          setAvailableBetTypes(betTypes);
          const isOverUnder = betTypes.some((type) =>
            ["Over", "Under"].includes(type)
          );
          if (!isOverUnder && betTypes.length > 0) {
            setSelectedBetType(betTypes[0]); // e.g., "Yes"
          } else {
            setSelectedBetType(null); // Wait for user selection
          }
        } catch (error) {
          console.error("Error fetching available bet types:", error);
        } finally {
          setBetTypesLoading(false);
        }
      };
      fetchAvailableBetTypes();
    }
  }, [selectedPlayer, selectedProp]);

  const handleSearchChange = useCallback(
    (event) => {
      const value = event.target.value;
      setSearchQuery(value);
    },
    [setSearchQuery]
  );

  const handlePlayerSelect = (playerName) => {
    if (playerName !== selectedPlayer) {
      setSelectedPlayer(playerName);
      setSelectedProp("");
      setUniqueBookies([]);
      setSelectedBookies([]);
      setAvailableBetTypes([]);
      setSelectedBetType(null);
    }
  };

  const updateBookies = useCallback(
    (bookies) => {
      setUniqueBookies(bookies);
      setSelectedBookies(bookies);
    },
    [setUniqueBookies, setSelectedBookies]
  );

  const toggleBookieSelection = (bookie) => {
    setSelectedBookies((prevSelected) =>
      prevSelected.includes(bookie)
        ? prevSelected.filter((b) => b !== bookie)
        : [...prevSelected, bookie]
    );
  };

  const handlePropTypeSelect = useCallback((prop) => {
    setSelectedProp(prop);
    setSelectedBetType(null);
    setUniqueBookies([]);
    setSelectedBookies([]);
  }, []);

  const filteredPlayerNames = playerNames.filter((name) =>
    name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const isOverUnderProp = availableBetTypes.some((type) =>
    ["Over", "Under"].includes(type)
  );

  if (loading || betTypesLoading) {
    return (
      <div style={{ textAlign: "center", marginTop: "20px" }}>
        <ClipLoader size={100} color="#007bff" />
        <p>Loading data... Please wait.</p>
      </div>
    );
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <div>
        {selectedPlayer ? (
          <>
            <h3 className="Prop-Player">Selected Player: {selectedPlayer}</h3>
            <button
              onClick={() => {
                setSelectedPlayer("");
                setSelectedProp("");
                setAvailableBetTypes([]);
                setSelectedBetType(null);
              }}
            >
              Clear Selected Player
            </button>
            <PropTypeDropdown
              selectedPlayer={selectedPlayer}
              selectedProp={selectedProp}
              onPropTypeSelect={handlePropTypeSelect}
            />

            {selectedProp && isOverUnderProp && (
              <div style={{ margin: "16px 0" }}>
                <label style={{ marginRight: "8px" }}>Select Bet Type: </label>
                <select
                  value={selectedBetType || ""}
                  onChange={(e) => setSelectedBetType(e.target.value)}
                  style={{ padding: "4px" }}
                >
                  <option value="" disabled>
                    Select Over or Under
                  </option>
                  {availableBetTypes
                    .filter((type) => ["Over", "Under"].includes(type))
                    .map((betType) => (
                      <option key={betType} value={betType}>
                        {betType}
                      </option>
                    ))}
                </select>
              </div>
            )}

            {selectedPlayer && selectedProp && !betTypesLoading && (
              <LatestPropsTable
                playerName={selectedPlayer}
                propType={selectedProp}
                selectedBetType={selectedBetType}
                isOverUnderProp={isOverUnderProp}
              />
            )}

            {uniqueBookies.length > 0 &&
              !betTypesLoading &&
              (!isOverUnderProp || selectedBetType !== null) && (
                <div style={{ textAlign: "center" }}>
                  <h4>Filter by Bookies:</h4>
                  <div className="bookie-checkboxes-container">
                    {uniqueBookies.map((bookie) => (
                      <label key={bookie} className="bookie-checkboxes">
                        <input
                          type="checkbox"
                          checked={selectedBookies.includes(bookie)}
                          onChange={() => toggleBookieSelection(bookie)}
                        />
                        {bookie}
                      </label>
                    ))}
                  </div>
                </div>
              )}

            {selectedProp &&
              !betTypesLoading &&
              (!isOverUnderProp || selectedBetType !== null) && (
                <div className="chart-wrapper">
                  <div className="chart-container">
                    <PropDataGraph
                      selectedPlayer={selectedPlayer}
                      selectedProp={selectedProp}
                      bet_type="betting_line"
                      bet_type_name="Betting Lines"
                      selectedBookies={selectedBookies}
                      updateBookies={updateBookies}
                      selectedBetType={selectedBetType}
                    />
                  </div>
                  <div className="chart-container">
                    <PropDataGraph
                      selectedPlayer={selectedPlayer}
                      selectedProp={selectedProp}
                      bet_type="betting_point"
                      bet_type_name="Betting Points"
                      selectedBookies={selectedBookies}
                      updateBookies={updateBookies}
                      selectedBetType={selectedBetType}
                    />
                  </div>
                </div>
              )}
          </>
        ) : (
          <>
            <input
              type="text"
              placeholder="Search player names..."
              value={searchQuery}
              onChange={handleSearchChange}
              style={{
                padding: "8px",
                marginTop: "16px",
                marginBottom: "16px",
                width: "25%",
                border: "1px solid #000",
              }}
            />
            {searchQuery && filteredPlayerNames.length > 0 && (
              <ul style={{ listStyleType: "none", paddingLeft: "0" }}>
                {filteredPlayerNames.map((player, index) => (
                  <li
                    key={index}
                    onClick={() => handlePlayerSelect(player)}
                    style={{
                      padding: "8px",
                      cursor: "pointer",
                      width: "25%",
                      backgroundColor: "#f0f0f0",
                      borderBottom: "1px solid #FFFFFF",
                    }}
                  >
                    {player}
                  </li>
                ))}
              </ul>
            )}
            {searchQuery && filteredPlayerNames.length === 0 && (
              <p>No players found.</p>
            )}
          </>
        )}
      </div>
    </div>
  );
};

PlayerProps.propTypes = {
  sportType: PropTypes.string.isRequired,
};

export default PlayerProps;
