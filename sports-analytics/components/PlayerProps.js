"use client";

import React, { useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";
import PropTypeDropdown from "./PropTypeDropdown"; // Importing PropTypeDropdown
import PropDataGraph from "./PropDataGraph"; // Importing PropDataGraph
import LatestPropsTable from "./LatestPropsTable";

const PlayerProps = ({ sportType }) => {
  const [playerNames, setPlayerNames] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState(""); // Player is selected here
  const [selectedProp, setSelectedProp] = useState(""); // New state for selected prop type
  const [uniqueBookies, setUniqueBookies] = useState([]); // Track unique bookies
  const [selectedBookies, setSelectedBookies] = useState([]); // Track selected checkboxes

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

        // Remove duplicates using a Set and sort alphabetically
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

  const handleSearchChange = useCallback(
    (event) => {
      const value = event.target.value;
      setSearchQuery(value);
    },
    [setSearchQuery]
  );

  const handlePlayerSelect = (playerName) => {
    if (playerName !== selectedPlayer) {
      setSelectedPlayer(playerName); // Set the selected player
      setSelectedProp(""); // Reset prop selection when a new player is chosen
      setUniqueBookies([]); // Clear bookies when player changes
      setSelectedBookies([]); // Reset selected checkboxes
    }
  };

  const updateBookies = useCallback(
    (bookies) => {
      setUniqueBookies(bookies);
      setSelectedBookies(bookies); // Default to selecting all bookies
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

  const filteredPlayerNames = playerNames.filter((name) =>
    name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return <div>Loading player names...</div>;
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
              }}
            >
              Clear Selected Player
            </button>
            {/* Render PropTypeDropdown and pass selectedPlayer and setSelectedProp */}
            <PropTypeDropdown
              selectedPlayer={selectedPlayer}
              selectedProp={selectedProp} // Pass current selected prop to the dropdown
              onPropTypeSelect={(prop) => {
                setSelectedProp(prop); // Update the selected prop in the parent
              }}
            />

            {selectedPlayer && selectedProp && (
              <LatestPropsTable
                playerName={selectedPlayer}
                propType={selectedProp}
              />
            )}

            {uniqueBookies.length > 0 && (
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

            {/* Conditionally render PropDataGraph when both player and prop are selected */}
            {selectedProp && (
              <div className="chart-wrapper">
                <div className="chart-container">
                  <PropDataGraph
                    selectedPlayer={selectedPlayer}
                    selectedProp={selectedProp}
                    bet_type="betting_line"
                    bet_type_name="Betting Lines"
                    selectedBookies={selectedBookies} // Pass selected bookies to graph
                    updateBookies={updateBookies} // Update bookies dynamically
                  />
                </div>
                <div className="chart-container">
                  <PropDataGraph
                    selectedPlayer={selectedPlayer}
                    selectedProp={selectedProp}
                    bet_type="betting_point"
                    bet_type_name="Betting Points"
                    selectedBookies={selectedBookies} // Pass selected bookies to graph
                    updateBookies={updateBookies} // Update bookies dynamically
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
