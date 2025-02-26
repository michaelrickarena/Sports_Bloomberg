"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { usePathname } from "next/navigation";
import Cookies from "js-cookie";
import styles from "../styles/NavBar.module.css";

const NavBar = () => {
  const router = useRouter();
  const pathname = usePathname();
  const [showDropdown, setShowDropdown] = useState(false);
  const [showDropdownNHL, setShowDropdownNHL] = useState(false);
  const [showDropdownMLB, setShowDropdownMLB] = useState(false);
  const [showDropdownNBA, setShowDropdownNBA] = useState(false);
  const [showDropdownAnalytics, setShowDropdownAnalytics] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = Cookies.get("access_token");
    setIsLoggedIn(!!token);
  }, [pathname]);

  const handleLogout = () => {
    Cookies.remove("access_token");
    Cookies.remove("refresh_token");
    setIsLoggedIn(false);
    router.push("/login");
  };

  const handleLogin = () => {
    setIsLoggedIn(true);
    Cookies.set("access_token", "your_access_token", { expires: 1 });
    router.push("/");
  };

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

        {/* Analytics Dropdown */}
        <li
          className={styles.navItem}
          onMouseEnter={() => setShowDropdownAnalytics(true)}
          onMouseLeave={() => setShowDropdownAnalytics(false)}
        >
          Analytics
          {showDropdownAnalytics && (
            <ul className={styles.dropdown}>
              <li>
                <Link href="/biggest-line-movements">
                  Biggest Line Movements
                </Link>
              </li>
              <li>
                <Link href="/arbitrage-opportunities">
                  Arbitrage Opportunities
                </Link>
              </li>
            </ul>
          )}
        </li>

        {/* User Authentication Links */}
        {isLoggedIn ? (
          <>
            <li className={`${styles.navItem} ${styles.rightAlign}`}>
              <Link href="/checkout">Subscribe</Link>
            </li>
            <li className={styles.navItem}>
              <Link href="/account">Account</Link> {/* New Item */}
            </li>
            <li className={`${styles.navItem}`}>
              <Link href="/" onClick={handleLogout}>
                Logout
              </Link>
            </li>
          </>
        ) : (
          // Not Logged In - Show Sign In and Sign Up
          <>
            <li className={`${styles.navItem} ${styles.rightAlign}`}>
              <Link href="/login">Sign In</Link>
            </li>
            <li className={styles.navItem}>
              <Link href="/register">Sign Up</Link>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
};

export default NavBar;
