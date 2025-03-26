import UserBetCreate from "../../components/userbets";
import MyBets from "../../components/userbets_list_delete";
import "../../styles/userbets.css"; // Global styles if needed

export default function ArbitrageOpportunitiesPage() {
  return (
    <main>
      <div className="arbitrage-tracking-sports-bets">
        <h2>Track Your Market Positions</h2>
        <h5 className="how-it-works">How This Works:</h5>
        <p>
          When you enter a moneyline market position, log the selection along
          with the amount.
        </p>
        <p>
          If you’re targeting a specific return (e.g., a 5% gain), set your
          alert threshold accordingly.
        </p>
        <p>
          Our system continuously monitors market prices from multiple sources.
          If conditions shift in your favor and meet your threshold, you’ll
          receive a notification.
        </p>
        <p>
          To ensure you don’t miss important alerts, add{" "}
          <strong>notifications@thesmartlines.com</strong> to your safe sender
          list so emails don’t end up in spam.
        </p>
        <div className="arbitrage-container">
          <UserBetCreate />
          <MyBets />
        </div>
      </div>
    </main>
  );
}
