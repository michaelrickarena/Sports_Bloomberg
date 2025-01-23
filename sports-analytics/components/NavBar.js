"use client"; // Add this line at the top of the file to mark this component as a client component

import React, { useState } from "react";
import Link from "next/link";
import styles from "../styles/NavBar.module.css";

const NavBar = () => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [showDropdownNHL, setShowDropdownNHL] = useState(false);
  const [showDropdownMLB, setShowDropdownMLB] = useState(false);
  const [showDropdownNBA, setShowDropdownNBA] = useState(false);

  return (
    <nav className={styles.nav}>
      <ul className={styles.navList}>
        <li className={styles.navItem}>
          <Link href="/">Home</Link>
        </li>

        {/* NFL Dropdown */}
        <li
          className={styles.navItem}
          onMouseEnter={() => setShowDropdown(true)}
          onMouseLeave={() => setShowDropdown(false)}
        >
          NFL
          {showDropdown && (
            <ul className={styles.dropdown}>
              <li>
                <Link href="/money-line-NFL">Money Line</Link>
              </li>
              <li>
                <Link href="/over-under-NFL">Over Under</Link>
              </li>
              <li>
                <Link href="/spreads-NFL">Spreads</Link>
              </li>
              <li>
                <Link href="/player-props-NFL">Player Props</Link>
              </li>
            </ul>
          )}
        </li>

        {/* NHL Dropdown */}
        <li
          className={styles.navItem}
          onMouseEnter={() => setShowDropdownNHL(true)}
          onMouseLeave={() => setShowDropdownNHL(false)}
        >
          NHL
          {showDropdownNHL && (
            <ul className={styles.dropdown}>
              <li>
                <Link href="/money-line-NHL">Money Line</Link>
              </li>
              <li>
                <Link href="/over-under-NHL">Over Under</Link>
              </li>
              <li>
                <Link href="/spreads-NHL">Spreads</Link>
              </li>
              <li>
                <Link href="/player-props-NHL">Player Props</Link>
              </li>
            </ul>
          )}
        </li>

        {/* MLB Dropdown */}
        <li
          className={styles.navItem}
          onMouseEnter={() => setShowDropdownMLB(true)}
          onMouseLeave={() => setShowDropdownMLB(false)}
        >
          MLB
          {showDropdownMLB && (
            <ul className={styles.dropdown}>
              <li>
                <Link href="/money-line-MLB">Money Line</Link>
              </li>
              <li>
                <Link href="/over-under-MLB">Over Under</Link>
              </li>
              <li>
                <Link href="/spreads-MLB">Spreads</Link>
              </li>
              <li>
                <Link href="/player-props-MLB">Player Props</Link>
              </li>
            </ul>
          )}
        </li>

        {/* NBA Dropdown */}
        <li
          className={styles.navItem}
          onMouseEnter={() => setShowDropdownNBA(true)}
          onMouseLeave={() => setShowDropdownNBA(false)}
        >
          NBA
          {showDropdownNBA && (
            <ul className={styles.dropdown}>
              <li>
                <Link href="/money-line-NBA">Money Line</Link>
              </li>
              <li>
                <Link href="/over-under-NBA">Over Under</Link>
              </li>
              <li>
                <Link href="/spreads-NBA">Spreads</Link>
              </li>
              <li>
                <Link href="/player-props-NBA">Player Props</Link>
              </li>
            </ul>
          )}
        </li>
      </ul>
    </nav>
  );
};

export default NavBar;
