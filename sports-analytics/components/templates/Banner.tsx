import Link from "next/link";

import { Button } from "../button/Button";
import { CTABanner } from "../cta/CTABanner";
import { Section } from "../layout/Section";

const Banner = () => (
  <Section>
    <CTABanner
      title="All services are included with every subscription!"
      subtitle="Start Your 7 Day Free Trial."
      button={
        <Link href="/register">
          <Button>Get Started</Button>
        </Link>
      }
    />
  </Section>
);

export { Banner };
