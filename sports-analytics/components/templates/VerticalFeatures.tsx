import { VerticalFeatureRow } from "../feature/VerticalFeatureRow";
import { Section } from "../layout/Section";

const VerticalFeatures = () => (
  <Section
    title="Powerful Tools for Profitable Betting Decisions"
    description="Unlock a competitive edge with real-time arbitrage alerts, data-driven EV analysis, intuitive trend tracking, and pro-level insights-all for just pennies a day."
  >
    <VerticalFeatureRow
      title="Expected Value (EV) Analysis"
      description="Identify high-return opportunities with data-driven precision. Find and benefit from mispriced opportunities before they disappear."
      image="/assets/images/expected_value_table.png"
      imageAlt="Second feature alt text"
      reverse
    />

    <VerticalFeatureRow
      title="Real-Time Arbitrage Alerts"
      description="Get instant notifications of market inefficiencies to act fast. Track line movements of your moneyline positions to gaurentee profits through arbitrage betting."
      image="/assets/images/arb_tracking.png"
      imageAlt="First feature alt text"
    />
    <VerticalFeatureRow
      title="Sports & Bookmaker Trends"
      description="Track performance over time with intuitive line graphs. Enter wagers at the right time and identify profitable patterns with ease."
      image="/assets/images/feature2.svg"
      imageAlt="Second feature alt text"
      reverse
    />
    <VerticalFeatureRow
      title="Affordable at $10/Month"
      description="Access premium analytics without the $300/month price tag. Perfect for both casual and professional bettors."
      image="/assets/images/feature2.svg"
      imageAlt="Third feature alt text"
    />
  </Section>
);

export { VerticalFeatures };
