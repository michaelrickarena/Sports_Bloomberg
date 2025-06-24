import Link from "next/link";

import { Background } from "../background/Background";
import { CenteredFooter } from "../footer/CenteredFooter";
import { Section } from "../layout/Section";
import { Logo } from "./Logo";

const Footer = () => (
  <Background color="bg-gray-100">
    <Section>
      <CenteredFooter logo={<></>} iconList={<></>}>
        <li className="mx-4">
          <Link href="/termsandconditions">Terms and Conditions</Link>
        </li>
        <li className="mx-4">
          <Link href="/blogs">Blogs</Link>
        </li>
        <li className="mx-4">
          <Link href="/">Learn More</Link>
        </li>
        <li className="mx-4">
          <Link href="/register">Start Free Trial</Link>
        </li>
      </CenteredFooter>
    </Section>
  </Background>
);

export { Footer };
