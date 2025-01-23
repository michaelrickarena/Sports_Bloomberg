import MoneyLine from "../../components/MoneyLine"; // Correct path to MoneyLine
import "../../styles/globals.css"; // Global styles if needed

export default function MoneyLinePage() {
  return (
    <>
      <main>
        <MoneyLine sportTitle="NFL" />
      </main>
    </>
  );
}
