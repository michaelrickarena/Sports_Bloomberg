// app/over-under/page.js
import PlayerProps from "../../components/PlayerProps"; // Correct path to OverUnder component
import "../../styles/globals.css"; // Global styles if needed

export default function PlayerPropsPage() {
  return (
    <main>
      <PlayerProps sportType="basketball_nba" />
    </main>
  );
}
