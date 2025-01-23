// app/over-under/page.js
import OverUnder from "../../components/OverUnder"; // Correct path to OverUnder component
import "../../styles/globals.css"; // Global styles if needed

export default function OverUnderPage() {
  return (
    <main>
      <OverUnder sportTitle="NBA" />
    </main>
  );
}
