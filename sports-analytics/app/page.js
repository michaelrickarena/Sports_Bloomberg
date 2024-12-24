// app/page.js (Root/Home Page)
import React from "react";
import Link from "next/link";

const HomePage = () => {
  return (
    <div>
      <h1>Welcome to the Sports Analytics Website</h1>
      <p>Choose an option from the navbar to explore sports data.</p>
      <Link href="/money-line">Go to Money Line</Link>
      <br />
      <Link href="/over-under">Go to Over Under</Link>
      <br />
      <Link href="/player-props">Go to Player Props</Link>
      <br />
      <Link href="/spreads">Go to Spreads</Link>
    </div>
  );
};

export default HomePage;
