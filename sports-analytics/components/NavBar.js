"use client"; // Add this line at the top of the file to mark this component as a client component

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation"; // Import the router
import { usePathname } from "next/navigation"; // For detecting route changes (alternative to useRouter)
import styles from "../styles/NavBar.module.css";

const NavBar = () => {
  const router = useRouter();
  const pathname = usePathname(); // Get the current path
  const [showDropdown, setShowDropdown] = useState(false);
  const [showDropdownNHL, setShowDropdownNHL] = useState(false);
  const [showDropdownMLB, setShowDropdownMLB] = useState(false);
  const [showDropdownNBA, setShowDropdownNBA] = useState(false);
  const [showDropdownAnalytics, setShowDropdownAnalytics] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false); // State to track login status

  // Check login status on component mount and when route changes
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      setIsLoggedIn(true); // User is logged in
    } else {
      setIsLoggedIn(false); // User is not logged in
    }
  }, [pathname]); // Re-run useEffect when the route changes

  const handleLogout = () => {
    // Remove the tokens from localStorage
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    // Update the login status
    setIsLoggedIn(false);

    // Redirect to login page
    router.push("/login"); // Redirect user to login page after logout
  };

  const handleLogin = () => {
    // Manually update the login state when the user logs in
    setIsLoggedIn(true);

    // Store the token in localStorage
    localStorage.setItem("access_token", "your_access_token");

    // Optionally, redirect after login
    router.push("/"); // Or route to a dashboard/home page after login
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
          // Logged In - Show Logout
          <li className={`${styles.navItem} ${styles.rightAlign}`}>
            <button onClick={handleLogout}>Logout</button>
          </li>
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
