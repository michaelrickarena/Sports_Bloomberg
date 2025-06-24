import Blog01Arbitrage from "../../../components/blogs/Blog-01-Arbitrage";
import { Footer } from "../../../components/templates/Footer";

export default function ArbitrageCalculatorPage() {
  return (
    <main className="min-h-screen bg-white py-12">
      <div className="max-w-5xl mx-auto px-4">
        <Blog01Arbitrage />
        <Footer />
      </div>
    </main>
  );
}
