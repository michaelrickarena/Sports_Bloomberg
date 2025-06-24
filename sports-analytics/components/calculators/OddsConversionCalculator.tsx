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

function decimalToFractional(decimal: number): string {
  const frac = decimal - 1;
  // Simple fraction approximation
  const denominator = 1000;
  const numerator = Math.round(frac * denominator);
  function gcd(a: number, b: number): number {
    return b ? gcd(b, a % b) : a;
  }
  const divisor = gcd(numerator, denominator);
  return `${numerator / divisor}/${denominator / divisor}`;
}

function fractionalToDecimal(fractional: string): number {
  const [num, denom] = fractional.split("/").map(Number);
  if (!isNaN(num) && !isNaN(denom) && denom !== 0) {
    return num / denom + 1;
  }
  return 1;
}

const OddsConversionCalculator = () => {
  const [input, setInput] = useState<string>("100");
  const [inputType, setInputType] = useState("american");
  const [decimal, setDecimal] = useState(americanToDecimal(100));
  const [american, setAmerican] = useState(100);
  const [fractional, setFractional] = useState(
    decimalToFractional(americanToDecimal(100))
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setInput(val);
    let dec = 1;
    if (inputType === "american") {
      const numVal = Number(val);
      dec = americanToDecimal(numVal);
      setDecimal(dec);
      setAmerican(numVal);
      setFractional(decimalToFractional(dec));
    } else if (inputType === "decimal") {
      const numVal = Number(val);
      dec = numVal;
      setDecimal(numVal);
      setAmerican(decimalToAmerican(numVal));
      setFractional(decimalToFractional(numVal));
    } else if (inputType === "fractional") {
      dec = fractionalToDecimal(val);
      setDecimal(dec);
      setAmerican(decimalToAmerican(dec));
      setFractional(val);
    }
  };

  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setInputType(e.target.value);
    setInput("");
    setDecimal(1);
    setAmerican(0);
    setFractional("0/1");
  };

  // Description and title outside the card for SEO and clarity
  const description = `\
The Odds Conversion Calculator lets you convert between American, Decimal, and Fractional odds formats. Enter odds in any format, and the calculator will instantly show the equivalent values in the other formats. This tool is useful for comparing lines across sportsbooks and understanding odds from different regions.`;

  return (
    <div className="max-w-2xl mx-auto my-10">
      <h2 className="text-3xl font-bold mb-2 text-gray-800">
        Odds Conversion Calculator
      </h2>
      <p className="mb-6 text-gray-700 text-justify text-base">{description}</p>
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
        <div className="mt-8 bg-blue-50 border border-blue-200 text-blue-900 px-6 py-4 rounded-lg text-center">
          <div className="mb-2">
            <span className="font-semibold">American:</span>{" "}
            {american > 0 ? "+" : ""}
            {american}
          </div>
          <div className="mb-2">
            <span className="font-semibold">Decimal:</span> {decimal.toFixed(3)}
          </div>
          <div>
            <span className="font-semibold">Fractional:</span> {fractional}
          </div>
        </div>
      </section>
    </div>
  );
};

export { OddsConversionCalculator };
