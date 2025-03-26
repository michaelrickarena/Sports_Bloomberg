"use client";

import React, { useState, useEffect } from "react";

const UserBetCreate = () => {
  const [sport, setSport] = useState("");
  const [games, setGames] = useState([]);
  const [selectedGame, setSelectedGame] = useState("");
  const [gameId, setGameId] = useState(""); // Store game_id
  const [teamOptions, setTeamOptions] = useState([]);
  const [team, setTeam] = useState("");
  const [betAmount, setBetAmount] = useState("");
  const [bookie, setBookie] = useState("");
  const [line, setLine] = useState("");
  const [alertThreshold, setAlertThreshold] = useState("");
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchGames = async () => {
      if (!sport) return;

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/upcoming_games/`
        );

        if (!response.ok) throw new Error("Failed to fetch games.");

        const data = await response.json();

        // Filter games by selected sport
        const filteredGames = data.filter((game) => game.sport_title === sport);
        setGames(filteredGames);
        setSelectedGame(""); // Reset game selection
        setGameId(""); // Reset game_id
        setTeamOptions([]); // Reset team selection
        setTeam("");
      } catch (err) {
        console.error(err);
        setError("Failed to fetch upcoming games.");
      }
    };

    fetchGames();
  }, [sport]);

  useEffect(() => {
    if (!selectedGame) return;

    // Find the selected game by comparing as strings
    const game = games.find((g) => String(g.game_id) === String(selectedGame));

    if (game) {
      setGameId(game.game_id); // Store game_id
      setTeamOptions([game.home_team, game.away_team]);
      setTeam("");

      console.log("Game selected:", game);
      console.log("game_id set:", game.game_id);
    }
  }, [selectedGame, games]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!team || !betAmount || !bookie || !line || !alertThreshold) {
      setError("All fields are required.");
      return;
    }

    const data = {
      game_id: gameId, // Include game_id
      team_bet_on: team,
      bet_type: "moneyline",
      bet_amount: parseFloat(betAmount),
      bookie,
      line,
      alert_threshold: parseInt(alertThreshold, 10),
    };

    console.log("Submitting bet with data:", data); // Debugging log

    const token = document.cookie.replace(
      /(?:(?:^|.*;\s*)access_token\s*=\s*([^;]*).*$)|^.*$/,
      "$1"
    );

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/user_bets/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(data),
          credentials: "include",
        }
      );

      if (!response.ok) throw new Error("Failed to create bet.");

      setSuccess("Bet created successfully!");
      setError("");
      setTeam("");
      setBetAmount("");
      setBookie("");
      setLine("");
      setAlertThreshold("");
      setSport("");
      setSelectedGame("");
      setGames([]);
      setTeamOptions([]);
    } catch (err) {
      console.error(err);
      setError("Failed to create bet. Please try again.");
    }
  };

  return (
    <div>
      <div>
        <form className="Submit-Bet-Form" onSubmit={handleSubmit}>
          <div>
            <label>Sport</label>
            <select value={sport} onChange={(e) => setSport(e.target.value)}>
              <option value="">Select Sport</option>
              <option value="NFL">NFL</option>
              <option value="NBA">NBA</option>
              <option value="MLB">MLB</option>
              <option value="NHL">NHL</option>
            </select>
          </div>

          {sport && (
            <div>
              <label>Game</label>
              <select
                value={selectedGame}
                onChange={(e) => setSelectedGame(e.target.value)}
              >
                <option value="">Select Game</option>
                {games.map((game) => (
                  <option key={game.game_id} value={game.game_id}>
                    {game.away_team} @ {game.home_team} (
                    {new Date(game.event_timestamp).toLocaleString()})
                  </option>
                ))}
              </select>
            </div>
          )}

          {selectedGame && (
            <div>
              <label>Team</label>
              <select value={team} onChange={(e) => setTeam(e.target.value)}>
                <option value="">Select Team</option>
                {teamOptions.map((teamOption) => (
                  <option key={teamOption} value={teamOption}>
                    {teamOption}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label>Market Type</label>
            <input type="text" value="Moneyline" readOnly />
          </div>

          <div>
            <label>Amount Wagered</label>
            <input
              type="number"
              value={betAmount}
              onChange={(e) => setBetAmount(e.target.value)}
            />
          </div>

          <div>
            <label>Bookie Used</label>
            <input
              type="text"
              value={bookie}
              onChange={(e) => setBookie(e.target.value)}
            />
          </div>

          <div>
            <label>Line</label>
            <p className="Arbitrage-Threshold-Explanation">
              The line you made your wager at (American odds only)
            </p>
            <input
              type="number"
              value={line}
              onChange={(e) => setLine(e.target.value)}
            />
          </div>

          <div>
            <label>Return Threshold</label>
            <p className="Arbitrage-Threshold-Explanation">
              Enter the percentage as a whole number (e.g., 5 for a 5% return
              alert).
            </p>
            <input
              type="number"
              value={alertThreshold}
              onChange={(e) => setAlertThreshold(e.target.value)}
            />
          </div>

          <button type="submit">Start Scanning</button>
        </form>

        {success && <p style={{ color: "green" }}>{success}</p>}
        {error && <p style={{ color: "red" }}>{error}</p>}
      </div>
    </div>
  );
};

export default UserBetCreate;
