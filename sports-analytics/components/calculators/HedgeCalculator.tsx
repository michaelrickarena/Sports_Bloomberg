"use client";

import { useState } from "react";

function americanToDecimal(odds: number): number {
  if (odds > 0) return odds / 100 + 1;
  if (odds < 0) return 100 / -odds + 1;
  return 1;
}

const HedgeCalculator = () => {
  const [origStake, setOrigStake] = useState<string>("");
  const [origOdds, setOrigOdds] = useState<string>("");
  const [hedgeOdds, setHedgeOdds] = useState<string>("");
  const [inputType, setInputType] = useState("american");
  const [result, setResult] = useState<{
    hedgeStake: number;
    profitIfOrig: number;
    profitIfHedge: number;
    guaranteed: number;
  } | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    let decOrig = 1;
    let decHedge = 1;
    if (inputType === "american") {
      decOrig = americanToDecimal(Number(origOdds));
      decHedge = americanToDecimal(Number(hedgeOdds));
    } else {
      decOrig = Number(origOdds);
      decHedge = Number(hedgeOdds);
    }
    const stake = Number(origStake);
    if (decOrig <= 1 || decHedge <= 1 || stake <= 0) {
      setResult(null);
      return;
    }
    // Hedge stake covers original payout
    const hedgeStake = (stake * decOrig) / decHedge;
    // Profit if original wins: payout from original - hedge stake
    const profitIfOrig = stake * decOrig - stake - hedgeStake;
    // Profit if hedge wins: payout from hedge - original stake
    const profitIfHedge = hedgeStake * decHedge - hedgeStake - stake;
    const guaranteed = Math.min(profitIfOrig, profitIfHedge);
    setResult({ hedgeStake, profitIfOrig, profitIfHedge, guaranteed });
  };

  // Description and title outside the card for SEO and clarity
  const description = `\
The Hedge Calculator helps you lock in profit or minimize loss by calculating optimal hedge amounts for your bets. Enter your original bet, odds, and potential hedge odds. The calculator will show how much to hedge and your guaranteed profit or minimized loss, making it easier to manage risk on open bets.`;

  return (
    <div className="max-w-2xl mx-auto my-10">
      <h2 className="text-3xl font-bold mb-2 text-gray-800">
        Hedge Calculator
      </h2>
      <p className="mb-6 text-gray-700 text-justify text-base">{description}</p>
      <section className="bg-white py-10 px-6 sm:px-10 rounded-2xl shadow-xl border border-gray-200">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="flex gap-2">
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Original Bet Stake ($)
              </label>
              <input
                type="number"
                min="1"
                step="any"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={origStake}
                onChange={(e) => setOrigStake(e.target.value)}
                required
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Original Bet Odds
              </label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={origOdds}
                onChange={(e) => setOrigOdds(e.target.value)}
                placeholder={inputType === "american" ? "+110" : "2.10"}
                required
              />
            </div>
          </div>
          <div className="flex gap-2">
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Hedge Odds (Opposite Side)
              </label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={hedgeOdds}
                onChange={(e) => setHedgeOdds(e.target.value)}
                placeholder={inputType === "american" ? "-130" : "1.77"}
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
              <span className="font-semibold">Hedge Stake:</span> $
              {result.hedgeStake.toFixed(2)}
            </div>
            <div className="mb-2">
              <span className="font-semibold">Profit if Original Wins:</span> $
              {result.profitIfOrig.toFixed(2)}
            </div>
            <div className="mb-2">
              <span className="font-semibold">Profit if Hedge Wins:</span> $
              {result.profitIfHedge.toFixed(2)}
            </div>
            <div>
              <span className="font-semibold">Guaranteed Return (min):</span> $
              {result.guaranteed.toFixed(2)}
            </div>
          </div>
        )}
      </section>
    </div>
  );
};

export { HedgeCalculator };
