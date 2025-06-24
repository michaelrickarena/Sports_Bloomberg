"use client";

import { Meta } from "../layout/Meta";
import { AppConfig } from "../utils/AppConfig";
import { Banner } from "./Banner";
import { Footer } from "./Footer";
import { Hero } from "./Hero";
import { Sponsors } from "./Sponsors";
import { VerticalFeatures } from "./VerticalFeatures";
import { FAQ } from "./FAQ";

const Base = () => (
  <div className="text-gray-600 antialiased">
    <Meta title={AppConfig.title} description={AppConfig.description} />
    <Hero />
    <Sponsors />
    <VerticalFeatures />
    <FAQ />
    <Banner />
    <Footer />
  </div>
);

export { Base };
