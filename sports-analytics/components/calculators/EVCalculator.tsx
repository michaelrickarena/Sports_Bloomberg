"use client";

import { useState } from "react";

function americanToDecimal(odds: number): number {
  if (odds > 0) return odds / 100 + 1;
  if (odds < 0) return 100 / -odds + 1;
  return 1;
}

const EVCalculator = () => {
  const [odds, setOdds] = useState<string>("");
  const [inputType, setInputType] = useState("american");
  const [prob, setProb] = useState<string>("");
  const [stake, setStake] = useState<string>("");
  const [result, setResult] = useState<{
    ev: number;
    evPct: number;
  } | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    let decOdds = 1;
    if (inputType === "american") {
      decOdds = americanToDecimal(Number(odds));
    } else {
      decOdds = Number(odds);
    }
    const winProb = Number(prob) / 100;
    const loseProb = 1 - winProb;
    const bet = Number(stake);
    if (decOdds <= 1 || winProb < 0 || winProb > 1 || bet <= 0) {
      setResult(null);
      return;
    }
    // EV = (Win_Prob * (Odds * Stake - Stake)) - (Lose_Prob * Stake)
    const ev = winProb * (decOdds * bet - bet) - loseProb * bet;
    const evPct = (ev / bet) * 100;
    setResult({ ev, evPct });
  };

  return (
    <div className="max-w-2xl mx-auto px-4">
      <h1 className="text-4xl font-extrabold text-gray-900 mb-2 text-center">
        Expected Value (EV) Calculator
      </h1>
      <p
        className="mb-8 text-lg text-gray-700 max-w-2xl mx-auto"
        style={{ textAlign: "justify" }}
      >
        Calculate the expected value (EV) of your sports bets by entering the
        odds, your win probability, and your bet size. This tool helps you
        determine whether a bet is profitable in the long run by showing your
        expected profit or loss per bet.
      </p>
      <section className="bg-white py-10 px-6 sm:px-10 rounded-2xl shadow-xl border border-gray-200">
        <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">
          EV (Expected Value) Calculator
        </h2>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="flex gap-2">
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Odds
              </label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={odds}
                onChange={(e) => setOdds(e.target.value)}
                placeholder={inputType === "american" ? "+110" : "2.10"}
                required
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Odds Format
              </label>
              <select
                className="w-full border border-gray-300 rounded-lg px-2 py-2 bg-white"
                value={inputType}
                onChange={(e) => setInputType(e.target.value)}
              >
                <option value="american">American</option>
                <option value="decimal">Decimal</option>
              </select>
            </div>
          </div>
          <div className="flex gap-2">
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Win Probability (%)
              </label>
              <input
                type="number"
                min="0"
                max="100"
                step="any"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={prob}
                onChange={(e) => setProb(e.target.value)}
                required
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Bet Size ($)
              </label>
              <input
                type="number"
                min="1"
                step="any"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={stake}
                onChange={(e) => setStake(e.target.value)}
                required
              />
            </div>
          </div>
          <button
            type="submit"
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 rounded-lg transition duration-200"
          >
            Calculate
          </button>
        </form>
        {result && (
          <div
            className={`mt-8 px-6 py-4 rounded-lg text-center border ${
              result.ev >= 0
                ? "bg-green-50 border-green-200 text-green-800"
                : "bg-red-50 border-red-200 text-red-700"
            }`}
          >
            <div className="mb-2">
              <span className="font-semibold">Expected Value (EV):</span> $
              {result.ev.toFixed(2)}
            </div>
            <div>
              <span className="font-semibold">EV as % of Stake:</span>{" "}
              {result.evPct.toFixed(2)}%
            </div>
          </div>
        )}
      </section>
    </div>
  );
};

export { EVCalculator };
