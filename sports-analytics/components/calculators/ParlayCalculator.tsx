"use client";

import { useState } from "react";

function americanToDecimal(odds: number): number {
  if (odds > 0) return odds / 100 + 1;
  if (odds < 0) return 100 / -odds + 1;
  return 1;
}

const ParlayCalculator = () => {
  const [legs, setLegs] = useState<string[]>([""]);
  const [inputType, setInputType] = useState("american");
  const [stake, setStake] = useState<string>("");
  const [result, setResult] = useState<{
    totalOdds: number;
    payout: number;
    totalAmerican?: number;
  } | null>(null);

  const handleLegChange = (idx: number, value: string) => {
    const newLegs = [...legs];
    newLegs[idx] = value;
    setLegs(newLegs);
  };

  const addLeg = () => setLegs([...legs, ""]);
  const removeLeg = (idx: number) =>
    setLegs(legs.length > 1 ? legs.filter((_, i) => i !== idx) : legs);

  const decimalToAmerican = (decimal: number): number => {
    if (decimal >= 2) return Math.round((decimal - 1) * 100);
    if (decimal > 1) return Math.round(-100 / (decimal - 1));
    return 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    let total = 1;
    for (const leg of legs) {
      let dec = 1;
      if (inputType === "american") {
        dec = americanToDecimal(Number(leg));
      } else {
        dec = Number(leg);
      }
      if (dec <= 1) {
        setResult(null);
        return;
      }
      total *= dec;
    }
    const bet = Number(stake);
    if (bet <= 0) {
      setResult(null);
      return;
    }
    const payout = bet * total;
    let totalAmerican = decimalToAmerican(total);
    setResult({ totalOdds: total, payout, totalAmerican });
  };

  // Description and title outside the card for SEO and clarity
  const description = `\
The Parlay Calculator helps you determine the total payout and implied probability for multi-leg bets. Enter the odds for each leg (American format), and the calculator will show the combined odds, implied probability, and potential payout. Use this tool to evaluate the risk and reward of your parlay bets.`;

  return (
    <div className="max-w-2xl mx-auto my-10">
      <h2 className="text-3xl font-bold mb-2 text-gray-800">
        Parlay Calculator
      </h2>
      <p className="mb-6 text-gray-700 text-justify text-base">{description}</p>
      <section className="bg-white py-10 px-6 sm:px-10 rounded-2xl shadow-xl border border-gray-200">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Odds Format
            </label>
            <select
              className="border border-gray-300 rounded-lg px-2 py-2 bg-white"
              value={inputType}
              onChange={(e) => setInputType(e.target.value)}
            >
              <option value="american">American</option>
              <option value="decimal">Decimal</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Parlay Legs
            </label>
            {legs.map((leg, idx) => (
              <div key={idx} className="flex gap-2 mb-2">
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  value={leg}
                  onChange={(e) => handleLegChange(idx, e.target.value)}
                  placeholder={inputType === "american" ? "+110" : "2.10"}
                  required
                />
                {legs.length > 1 && (
                  <button
                    type="button"
                    className="bg-red-100 text-red-700 rounded px-2 py-1 text-xs font-semibold hover:bg-red-200"
                    onClick={() => removeLeg(idx)}
                    aria-label="Remove leg"
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              className="mt-2 bg-blue-100 text-blue-700 rounded px-3 py-1 text-sm font-semibold hover:bg-blue-200"
              onClick={addLeg}
            >
              + Add Leg
            </button>
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Bet Amount ($)
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
          <button
            type="submit"
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 rounded-lg transition duration-200"
          >
            Calculate
          </button>
        </form>
        {result && (
          <div className="mt-8 bg-blue-50 border border-blue-200 text-blue-900 px-6 py-4 rounded-lg text-center">
            <div className="mb-2">
              {inputType === "american" ? (
                <>
                  <span className="font-semibold">
                    Total Parlay Odds (American):
                  </span>{" "}
                  {result.totalAmerican > 0 ? "+" : ""}
                  {result.totalAmerican}
                </>
              ) : (
                <>
                  <span className="font-semibold">
                    Total Parlay Odds (Decimal):
                  </span>{" "}
                  {result.totalOdds.toFixed(3)}
                </>
              )}
            </div>
            <div>
              <span className="font-semibold">Total Payout:</span> $
              {result.payout.toFixed(2)}
            </div>
          </div>
        )}
      </section>
    </div>
  );
};

export { ParlayCalculator };
