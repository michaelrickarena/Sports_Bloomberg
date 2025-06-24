"use client";

import { useState } from "react";

// Helper to convert American odds to decimal odds
function americanToDecimal(odds: number): number {
  if (odds > 0) return 1 + odds / 100;
  if (odds < 0) return 1 - 100 / odds;
  return 0;
}

const ArbitrageCalculator = () => {
  const [odds1, setOdds1] = useState("");
  const [odds2, setOdds2] = useState("");
  const [stake, setStake] = useState("");
  const [result, setResult] = useState<{
    stake1: number;
    stake2: number;
    profit: number;
  } | null>(null);
  const [showError, setShowError] = useState(false);

  const calculateArb = (e: React.FormEvent) => {
    e.preventDefault();
    setShowError(false);
    const numOdds1 = Number(odds1);
    const numOdds2 = Number(odds2);
    const numStake = Number(stake);
    if (!odds1 || !odds2 || !stake) {
      setResult(null);
      return;
    }
    const decOdds1 = americanToDecimal(numOdds1);
    const decOdds2 = americanToDecimal(numOdds2);
    if (!decOdds1 || !decOdds2 || decOdds1 <= 1 || decOdds2 <= 1) {
      setResult(null);
      setShowError(true);
      return;
    }
    const prob1 = 1 / decOdds1;
    const prob2 = 1 / decOdds2;
    const totalProb = prob1 + prob2;
    if (totalProb >= 1) {
      setResult(null);
      setShowError(true);
      return;
    }
    // Corrected stake calculations
    const stake1 = (numStake * prob1) / totalProb;
    const stake2 = (numStake * prob2) / totalProb;
    const payout1 = stake1 * decOdds1;
    const payout2 = stake2 * decOdds2;
    const profit = Math.min(payout1, payout2) - numStake;
    setResult({ stake1, stake2, profit });
  };

  return (
    <div className="max-w-2xl mx-auto px-4">
      <h1 className="text-4xl font-extrabold text-gray-900 mb-2 text-center">
        Arbitrage Calculator
      </h1>
      <p
        className="mb-8 text-lg text-gray-700 text-center max-w-2xl mx-auto"
        style={{ textAlign: "justify" }}
      >
        Use this free arbitrage calculator to calculate exact bet amounts for
        guaranteed profit, no matter the outcome. Just enter the American odds
        from both sportsbooks and your total stake. The calculator instantly
        shows how much to bet on each side to lock in a risk-free return.
        Arbitrage betting takes advantage of odds discrepancies between
        sportsbooks, helping you secure consistent, no-risk gains.
      </p>
      <section className="bg-white py-10 px-6 sm:px-10 rounded-2xl shadow-xl border border-gray-200">
        <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">
          Arbitrage Calculator{" "}
          <span className="text-base text-gray-500">(American Odds)</span>
        </h2>

        <form onSubmit={calculateArb} className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Odds 1 (American)
            </label>
            <input
              type="number"
              step="any"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={odds1}
              onChange={(e) => setOdds1(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Odds 2 (American)
            </label>
            <input
              type="number"
              step="any"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={odds2}
              onChange={(e) => setOdds2(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Total Stake
            </label>
            <input
              type="number"
              step="any"
              min="1"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={stake}
              onChange={(e) => setStake(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 rounded-lg transition duration-200"
          >
            Calculate
          </button>
        </form>

        {result && !showError && (
          <div className="mt-8 bg-green-50 border border-green-200 text-green-800 px-6 py-4 rounded-lg text-center">
            <p className="mb-1">
              Stake on Odds 1:{" "}
              <span className="font-bold">${result.stake1.toFixed(2)}</span>
            </p>
            <p className="mb-1">
              Stake on Odds 2:{" "}
              <span className="font-bold">${result.stake2.toFixed(2)}</span>
            </p>
            <p className="mt-3 text-lg font-semibold">
              Guaranteed Profit: ${result.profit.toFixed(2)}
            </p>
          </div>
        )}

        {showError && odds1 && odds2 && stake && (
          <div className="mt-6 bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg text-center">
            No arbitrage opportunity with these odds.
          </div>
        )}
      </section>
    </div>
  );
};

export { ArbitrageCalculator };
