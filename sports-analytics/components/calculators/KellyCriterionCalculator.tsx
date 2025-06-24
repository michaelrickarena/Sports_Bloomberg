"use client";

import { useState, useEffect } from "react";

const KellyCriterionCalculator = () => {
  const [bankroll, setBankroll] = useState(1000);
  const [odds, setOdds] = useState(0);
  const [prob, setProb] = useState(0);
  const [result, setResult] = useState<number | null>(null);
  const [impliedProb, setImpliedProb] = useState(0);
  const [probEdited, setProbEdited] = useState(false);

  // Convert American odds to decimal odds
  function americanToDecimal(odds: number): number {
    if (odds > 0) return 1 + odds / 100;
    if (odds < 0) return 1 - 100 / odds;
    return 0;
  }

  // Convert American odds to implied probability (%)
  function americanToProbability(odds: number): number {
    if (odds > 0) return (100 / (odds + 100)) * 100;
    if (odds < 0) return (-odds / (-odds + 100)) * 100;
    return 0;
  }

  useEffect(() => {
    if (!probEdited) {
      const implied = americanToProbability(odds);
      setImpliedProb(implied);
      setProb(Number(implied.toFixed(2)));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [odds]);

  const handleProbChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProb(Number(e.target.value));
    setProbEdited(true);
  };

  const handleOddsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setOdds(Number(e.target.value));
    setProbEdited(false);
  };

  const calculateKelly = (e: React.FormEvent) => {
    e.preventDefault();
    const decOdds = americanToDecimal(odds);
    if (!bankroll || !decOdds || !prob) {
      setResult(null);
      return;
    }
    const b = decOdds - 1;
    const p = prob / 100;
    const q = 1 - p;
    const kellyFraction = (b * p - q) / b;
    const stake = Math.max(0, kellyFraction * bankroll);
    setResult(stake);
  };

  // Description and title outside the card for SEO and clarity
  const description = `\
The Kelly Criterion Calculator helps you determine the optimal bet size for maximizing long-term growth based on your edge and bankroll. Enter your bankroll, odds (American), and your estimated win probability. The calculator will suggest the ideal stake to maximize expected growth while minimizing risk of ruin. Adjust the win probability if your estimate differs from the implied probability.`;

  return (
    <div className="max-w-2xl mx-auto my-10">
      <h2 className="text-3xl font-bold mb-2 text-gray-800">
        Kelly Criterion Calculator{" "}
        <span className="text-base text-gray-500">(American Odds)</span>
      </h2>
      <p className="mb-6 text-gray-700 text-justify text-base">{description}</p>
      <section className="bg-white py-10 px-6 sm:px-10 rounded-2xl shadow-xl border border-gray-200">
        <form onSubmit={calculateKelly} className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Bankroll ($)
            </label>
            <input
              type="number"
              min="1"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={bankroll}
              onChange={(e) => setBankroll(Number(e.target.value))}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Odds (American)
            </label>
            <input
              type="number"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={odds || ""}
              onChange={handleOddsChange}
              required
            />
            <span className="text-sm text-gray-500 mt-1 block">
              Implied Win Probability:{" "}
              {impliedProb ? impliedProb.toFixed(2) : "0.00"}%
            </span>
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Win Probability (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="any"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={prob || ""}
              onChange={handleProbChange}
              required
            />
            <span className="text-xs text-gray-500 mt-1 block">
              (You can adjust this if your estimate differs from the implied
              probability.)
            </span>
            {Math.abs(prob - impliedProb) < 0.01 && (
              <div className="mt-2 text-xs text-yellow-600 bg-yellow-50 border border-yellow-200 rounded px-2 py-1">
                Your win probability matches the implied probability. Kelly
                stake will be near zero unless you have an edge.
              </div>
            )}
          </div>
          <button
            type="submit"
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 rounded-lg transition duration-200"
          >
            Calculate
          </button>
        </form>
        {result !== null && (
          <div className="mt-8 bg-green-50 border border-green-200 text-green-800 px-6 py-4 rounded-lg text-center">
            <div>
              Recommended Stake:{" "}
              <span
                className={`font-bold ${result < 1 ? "text-yellow-700" : ""}`}
              >
                ${result.toFixed(2)}
              </span>
            </div>
            {result < 1 && (
              <p className="text-sm text-gray-600 mt-2">
                Low stake suggests your win probability is close to the implied
                probability ({impliedProb.toFixed(2)}%). Increase your estimated
                probability for a larger bet.
              </p>
            )}
          </div>
        )}
      </section>
    </div>
  );
};

export { KellyCriterionCalculator };
