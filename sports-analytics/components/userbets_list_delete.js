"use client";

import React, { useState, useEffect } from "react";

const MyBets = () => {
  const [bets, setBets] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBets = async () => {
      try {
        const token = document.cookie.replace(
          /(?:(?:^|.*;\s*)access_token\s*=\s*([^;]*).*$)|^.*$/,
          "$1"
        );

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/user_bets/list/`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
            credentials: "include",
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch bets: ${response.statusText}`);
        }

        const data = await response.json();
        console.log("Fetched bets from API:", data); // Debugging
        setBets(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchBets();
  }, []);

  const handleDelete = async (betId) => {
    console.log("Current bets in state:", bets);
    console.log("Trying to delete bet with ID:", betId);
    console.log("Attempting to delete bet with ID:", betId); // Debugging

    try {
      const token = document.cookie.replace(
        /(?:(?:^|.*;\s*)access_token\s*=\s*([^;]*).*$)|^.*$/,
        "$1"
      );

      const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/user_bets/delete/${betId}/`;
      console.log("DELETE request URL:", apiUrl); // Debugging

      const response = await fetch(apiUrl, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        credentials: "include",
      });

      if (!response.ok) {
        console.error(
          "Failed to delete bet. Response status:",
          response.status
        );
        throw new Error("Failed to delete bet");
      }

      // Filter bets using string comparison
      setBets(bets.filter((bet) => bet.id !== betId));
      console.log("Bet successfully deleted:", betId); // Debugging
    } catch (err) {
      console.error("Error deleting bet:", err.message);
      setError(err.message);
    }
  };

  const renderBets = () => {
    if (loading) {
      return <p>Loading...</p>;
    }

    if (error) {
      return <p style={{ color: "red" }}>{error}</p>;
    }

    if (bets.length === 0) {
      return (
        <p className="no-bets">
          No bets currently being monitored - Record a bet and refresh.
        </p>
      );
    }

    return (
      <div className="bet-list">
        <ul>
          {bets.map((bet) => (
            <li key={bet.id} className="bet-item">
              <div>
                <strong>Bookie Used: </strong> {bet.bookie || "N/A"}
                <br />
                <strong>Wagered Team: </strong> {bet.team_bet_on || "N/A"}
                <br />
                <strong>Bet Line: </strong> {bet.line || "N/A"}
                <br />
                <strong>Bet Amount: </strong>${bet.bet_amount || "N/A"}
                <br />
                <strong>Alert Threshold: </strong>{" "}
                {bet.alert_threshold || "N/A"}%
                <br />
                <button onClick={() => handleDelete(bet.id)}>Remove Bet</button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div>
      <h2 className="bet-list-title">Currently Scanning for Arbitrage:</h2>
      {renderBets()}
    </div>
  );
};

export default MyBets;
