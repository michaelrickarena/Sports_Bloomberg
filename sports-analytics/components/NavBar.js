// components/NavBar.js
"use client"; // Add this line at the top of the file to mark this component as a client component

import React, { useState } from "react";
import Link from "next/link";
import styles from "../styles/NavBar.module.css";

const NavBar = () => {
  const [showDropdown, setShowDropdown] = useState(false);

  return (
    <nav className={styles.nav}>
      <ul className={styles.navList}>
        <li className={styles.navItem}>
          <Link href="/">Home</Link>
        </li>
        <li
          className={styles.navItem}
          onMouseEnter={() => setShowDropdown(true)}
          onMouseLeave={() => setShowDropdown(false)}
        >
          NFL
          {showDropdown && (
            <ul className={styles.dropdown}>
              <li>
                <Link href="/money-line">Money Line</Link>
              </li>
              <li>
                <Link href="/over-under">Over Under</Link>
              </li>
              <li>
                <Link href="/player-props">Player Props</Link>
              </li>
              <li>
                <Link href="/spreads">Spreads</Link>
              </li>
            </ul>
          )}
        </li>
      </ul>
    </nav>
  );
};

export default NavBar;
