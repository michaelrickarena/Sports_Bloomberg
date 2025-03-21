"use client";
import React, { useState, useEffect } from "react";

const PropTypeDropdown = ({
  selectedPlayer,
  selectedProp,
  onPropTypeSelect,
}) => {
  const [propTypes, setPropTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPlayer, setCurrentPlayer] = useState(null);

  useEffect(() => {
    if (!selectedPlayer || selectedPlayer === currentPlayer) {
      return; // Prevent fetching again if the player hasn't changed
    }

    setCurrentPlayer(selectedPlayer);

    const fetchPropTypes = async () => {
      setLoading(true);

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/latest_props/?player_name=${selectedPlayer}`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch prop types");
        }

        const data = await response.json();

        // Ensure data.results is an array and filter out invalid entries
        const validPropTypes = (data.results || []).filter(
          (prop) => typeof prop === "string" && prop.length > 0
        ); // Only keep valid strings
        setPropTypes([...new Set(validPropTypes)]); // Remove duplicates
      } catch (error) {
        console.error("Error fetching prop types:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPropTypes();
  }, [selectedPlayer, currentPlayer]);

  const handleChange = (event) => {
    const selectedValue = event.target.value;
    onPropTypeSelect(selectedValue); // Notify the parent component directly
  };

  return (
    <div>
      {loading ? (
        <div>Loading prop types...</div>
      ) : propTypes.length > 0 ? (
        <select value={selectedProp || ""} onChange={handleChange}>
          <option value="" disabled>
            Select a prop type
          </option>
          {propTypes.map((prop, index) => (
            <option key={index} value={prop}>
              {prop
                .replace(/_/g, " ") // Replace underscores with spaces
                .replace(/\b\w/g, (char) => char.toUpperCase())}{" "}
              {/* Capitalize each word */}
            </option>
          ))}
        </select>
      ) : (
        <p>No props found for this player.</p>
      )}
    </div>
  );
};

export default PropTypeDropdown;
