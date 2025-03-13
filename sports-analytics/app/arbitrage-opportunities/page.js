import UserBetCreate from "../../components/userbets";
import MyBets from "../../components/userbets_list_delete";
import "../../styles/userbets.css"; // Global styles if needed

export default function ArbitrageOpportunitiesPage() {
  return (
    <main>
      <h2>Record Your Bet For Arbitrage Monitoring</h2>
      <h5 className="how-it-works">How This Works:</h5>
      <p>
        When you place a live moneyline bet, log it here along with the amount
        wagered.
      </p>
      <p>{`If you're targeting a specific return for arbitrage (e.g., a 5% gain), set your alert threshold accordingly.`}</p>
      <p>
        Our system frequently scans available odds from all bookies. If the
        lines shift in your favor and meet your threshold, you’ll receive a
        notification.
      </p>
      <p>
        To ensure you don’t miss important alerts, add{" "}
        <strong>smartlinesinbox@gmail.com</strong> to your safe sender list to
        ensure emails dont end up in junk.
      </p>
      <div className="arbitrage-container">
        <UserBetCreate />
        <MyBets />
      </div>
    </main>
  );
}
