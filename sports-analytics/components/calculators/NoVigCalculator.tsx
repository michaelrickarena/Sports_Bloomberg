"use client";

import { useState } from "react";

function americanToDecimal(odds: number): number {
  if (odds > 0) return odds / 100 + 1;
  if (odds < 0) return 100 / -odds + 1;
  return 1;
}

function decimalToAmerican(decimal: number): number {
  if (decimal >= 2) return Math.round((decimal - 1) * 100);
  if (decimal > 1) return Math.round(-100 / (decimal - 1));
  return 0;
}

const NoVigCalculator = () => {
  const [oddsA, setOddsA] = useState<string>("");
  const [oddsB, setOddsB] = useState<string>("");
  const [inputType, setInputType] = useState("american");
  const [result, setResult] = useState<{
    fairDecimalA: number;
    fairDecimalB: number;
    fairAmericanA: number;
    fairAmericanB: number;
  } | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    let decA = 1;
    let decB = 1;
    if (inputType === "american") {
      decA = americanToDecimal(Number(oddsA));
      decB = americanToDecimal(Number(oddsB));
    } else {
      decA = Number(oddsA);
      decB = Number(oddsB);
    }
    if (decA <= 1 || decB <= 1) {
      setResult(null);
      return;
    }
    const pA = 1 / decA;
    const pB = 1 / decB;
    const total = pA + pB;
    const fairPA = pA / total;
    const fairPB = pB / total;
    const fairDecimalA = 1 / fairPA;
    const fairDecimalB = 1 / fairPB;
    const fairAmericanA = decimalToAmerican(fairDecimalA);
    const fairAmericanB = decimalToAmerican(fairDecimalB);
    setResult({ fairDecimalA, fairDecimalB, fairAmericanA, fairAmericanB });
  };

  // Description and title outside the card for SEO and clarity
  const description = `\
The No-Vig Calculator removes the sportsbook's margin (vig) from betting odds to reveal the true implied probability of each outcome. Enter the odds for both sides, and the calculator will show the fair probabilities and fair odds, helping you identify value bets and compare lines across sportsbooks.`;

  return (
    <div className="max-w-2xl mx-auto my-10">
      <h2 className="text-3xl font-bold mb-2 text-gray-800">
        No-Vig Calculator
      </h2>
      <p className="mb-6 text-gray-700 text-justify text-base">{description}</p>
      <section className="bg-white py-10 px-6 sm:px-10 rounded-2xl shadow-xl border border-gray-200">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="flex gap-2">
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Odds for Outcome A
              </label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={oddsA}
                onChange={(e) => setOddsA(e.target.value)}
                placeholder={inputType === "american" ? "+110" : "2.10"}
                required
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Odds for Outcome B
              </label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={oddsB}
                onChange={(e) => setOddsB(e.target.value)}
                placeholder={inputType === "american" ? "-130" : "1.77"}
                required
              />
            </div>
          </div>
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
              <span className="font-semibold">Fair Odds (Outcome A):</span>{" "}
              {result.fairDecimalA.toFixed(3)} (Decimal),{" "}
              {result.fairAmericanA > 0 ? "+" : ""}
              {result.fairAmericanA} (American)
            </div>
            <div>
              <span className="font-semibold">Fair Odds (Outcome B):</span>{" "}
              {result.fairDecimalB.toFixed(3)} (Decimal),{" "}
              {result.fairAmericanB > 0 ? "+" : ""}
              {result.fairAmericanB} (American)
            </div>
          </div>
        )}
      </section>
    </div>
  );
};

export { NoVigCalculator };
