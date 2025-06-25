import Image from "next/image";

const Sponsors = () => (
  <section className="bg-white py-16">
    <div className="max-w-5xl mx-auto text-center px-4">
      <h2 className="text-3xl font-extrabold text-gray-900 mb-4">
        Stop Missing Out on Profitable Opportunities
      </h2>
      <p className="text-lg text-gray-700 mb-8 text-justify">
        Tired of inconsistent betting decisions or paying $300/month for
        analytics tools? TheSmartlines empowers you with Expected Value (EV)
        analysis, arbitrage opportunities, custom filters, and clear trend
        visualizations for just $10/month covering over 20 bookies. Our platform
        has been backtested on millions of past bets to ensure optimal
        performance. Make smarter, more profitable choices without breaking the
        bank.
      </p>
      <div className="flex justify-center">
        <Image
          src="/assets/images/Celebrate.png"
          alt="Sports analytics dashboard screenshot"
          width={1200}
          height={800}
          className="shadow-lg rounded-lg"
          priority
        />
      </div>
    </div>
  </section>
);

export { Sponsors };
