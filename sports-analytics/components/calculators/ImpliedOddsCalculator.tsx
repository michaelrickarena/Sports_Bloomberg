"use client";

import { useState } from "react";

function americanToImplied(odds: number): number {
  if (odds > 0) return 100 / (odds + 100);
  if (odds < 0) return -odds / (-odds + 100);
  return 0;
}

function decimalToImplied(decimal: number): number {
  if (decimal > 1) return 1 / decimal;
  return 0;
}

function fractionalToImplied(fractional: string): number {
  const [num, denom] = fractional.split("/").map(Number);
  if (!isNaN(num) && !isNaN(denom) && denom !== 0) {
    return 1 / (num / denom + 1);
  }
  return 0;
}

const ImpliedOddsCalculator = () => {
  const [input, setInput] = useState<string>("");
  const [inputType, setInputType] = useState("american");
  const [implied, setImplied] = useState<number | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
    let prob = 0;
    if (inputType === "american") {
      const numVal = Number(e.target.value);
      prob = americanToImplied(numVal);
    } else if (inputType === "decimal") {
      const numVal = Number(e.target.value);
      prob = decimalToImplied(numVal);
    } else if (inputType === "fractional") {
      prob = fractionalToImplied(e.target.value);
    }
    setImplied(prob);
  };

  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setInputType(e.target.value);
    setInput("");
    setImplied(null);
  };

  return (
    <div className="max-w-2xl mx-auto my-12">
      <h1 className="text-3xl font-bold mb-2 text-gray-900">
        Implied Odds Calculator
      </h1>
      <p className="mb-6 text-gray-700 text-justify text-base sm:text-lg">
        Enter odds in American, Decimal, or Fractional format to instantly see
        the implied probability of a bet. This helps you understand what the
        odds say about the chance of winning, and compare your own estimates to
        the sportsbook&apos;s. Implied probability is a key concept for value
        betting and finding edges.
      </p>
      <section className="bg-white py-10 px-6 sm:px-10 rounded-2xl shadow-xl border border-gray-200">
        <form className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Enter Odds
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={input}
                onChange={handleInputChange}
                placeholder={inputType === "fractional" ? "e.g. 5/2" : ""}
              />
              <select
                className="border border-gray-300 rounded-lg px-2 py-2 bg-white"
                value={inputType}
                onChange={handleTypeChange}
              >
                <option value="american">American</option>
                <option value="decimal">Decimal</option>
                <option value="fractional">Fractional</option>
              </select>
            </div>
          </div>
        </form>
        {implied !== null && (
          <div className="mt-8 bg-blue-50 border border-blue-200 text-blue-900 px-6 py-4 rounded-lg text-center">
            <span className="font-semibold">Implied Probability:</span>{" "}
            {(implied * 100).toFixed(2)}%
          </div>
        )}
      </section>
    </div>
  );
};

export { ImpliedOddsCalculator };
