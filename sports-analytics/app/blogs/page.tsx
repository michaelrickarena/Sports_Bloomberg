import BlogHome from "../../components/blogs/blog-home";
import { Footer } from "../../components/templates/Footer";

// Next.js App Router SEO metadata export
export const metadata = {
  title: "The Smart Lines | Sports Betting Blog & Analytics Insights",
  description:
    "Explore The Smart Lines sports betting blog for expert insights, strategies, and analytics. Learn about arbitrage, expected value (EV), Kelly criterion, and advanced betting tools. Stay updated with the latest trends, calculators, and actionable tips to maximize your betting edge.",
};

export default function ArbitrageCalculatorPage() {
  return (
    <main className="min-h-screen bg-white py-12">
      <div className="max-w-5xl mx-auto px-4">
        <BlogHome />
        <Footer />
      </div>
    </main>
  );
}
