const faqs = [
  {
    question: "What is expected value (EV) in sports betting?",
    answer:
      "Expected value is a way to measure the potential profitability of a bet. It compares the odds being offered by a sportsbook to the actual probability of that outcome. A positive EV (+EV) bet means that, over time, you'd expect to profit by making that same bet repeatedly. Our platform highlights these opportunities so you can make smarter, data-driven bets.",
  },
  {
    question: "What is arbitrage betting?",
    answer:
      "Arbitrage betting is when you place bets on all outcomes of a game (using different sportsbooks) in a way that guarantees a profit, no matter the result. This is possible because different sportsbooks sometimes offer significantly different odds for the same event. We automatically detect these opportunities and tell you exactly how much to bet on each bookie.",
  },
  {
    question: "How often is the data updated?",
    answer:
      "We scan and analyze over 80,000 betting lines every 30 minutes, ensuring you always have the most up-to-date odds, arbitrage opportunities, and expected value bets. This is done to ensure a fair cost can always be offered although we plan to increase it to every 10 minutes to ensure even more up to date data",
  },
  {
    question: "Does this guarantee I’ll make money?",
    answer:
      "No system can guarantee profits in sports betting. While expected value and arbitrage strategies are proven ways to gain an edge over time, variance (luck) still plays a role in short-term outcomes. Our tools are designed to help maximize your edge and make smarter bets, not eliminate all risk.",
  },
  {
    question: "Can I track my own bets on the platform?",
    answer:
      "Yes! You can track your moneyline bets and we'll notify you if an arbitrage opportunity becomes available, or if line movements shift the value of your wager.",
  },
  {
    question: "Can beginners use this platform?",
    answer:
      "Absolutely. Whether you're a seasoned bettor or new to sports betting, our platform is built to be user-friendly. We break down each bet’s logic and value, and provide clear instructions for arbitrage opportunities.",
  },
  {
    question: "What does the Z-score mean for expected value bets?",
    answer:
      "The Z-score measures how far a sportsbook’s odds deviate from the market consensus, expressed in standard deviations. A more extreme Z-score (e.g., -2 or +2) indicates the line is highly mispriced compared to the expected probability. For example, a Z-score of -2 means the odds are two standard deviations different what’s expected — suggesting a strong value opportunity if your model is accurate.",
  },
];

const FAQ = () => (
  <section className="bg-white py-16">
    <div className="max-w-5xl mx-auto px-4">
      <h2 className="text-3xl font-extrabold text-gray-900 mb-8 text-center">
        Your Frequently Asked Questions, Answered
      </h2>
      <div className="space-y-6">
        {faqs.map((faq, idx) => (
          <div
            key={idx}
            className="border border-gray-200 rounded-lg p-6 bg-gray-50 shadow-sm"
          >
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              {faq.question}
            </h3>
            <p className="text-gray-700 text-base">{faq.answer}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

export { FAQ };
