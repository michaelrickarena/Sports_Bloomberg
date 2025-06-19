"use client";
import Link from "next/link";

import { Background } from "../background/Background";
import { Button } from "../button/Button";
import { HeroOneButton } from "../hero/HeroOneButton";
import { Section } from "../layout/Section";
import { Logo } from "./Logo";

const Hero = () => (
  <Background color="bg-gray-100">
    <Section yPadding="pt-10 pb-22">
      <div className="bg-gray-100 rounded-xl py-12">
        <HeroOneButton
          title={
            <>
              Unlock Profitable Sports Insights for Just{" "}
              <span className="text-primary-500">$10/Month</span>
            </>
          }
          description="TheSmartlines is your bookie analytics hub, delivering Expected Value (EV) bet analysis, real-time arbitrage alerts, and trend tracking to maximize your sports decisions—all for just pennies per day."
          button={
            <Link href="/register">
              <Button xl>Start your 7 day free trial now</Button>
            </Link>
          }
        />
      </div>
    </Section>
  </Background>
);

export { Hero };
