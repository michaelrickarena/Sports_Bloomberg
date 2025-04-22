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
  const [showDropdownArbitrage, setShowDropdownArbitrage] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    const token = Cookies.get("access_token");
    setIsLoggedIn(!!token);
  }, [pathname]);

  useEffect(() => {
    if (isMounted) {
      setIsMenuOpen(false);
      setShowDropdown(false);
      setShowDropdownNHL(false);
      setShowDropdownMLB(false);
      setShowDropdownNBA(false);
      setShowDropdownArbitrage(false);
    }
  }, [pathname, isMounted]);

  const handleLogout = () => {
    Cookies.remove("access_token");
    Cookies.remove("refresh_token");
    localStorage.removeItem("subscription_status");
    setIsLoggedIn(false);
    router.push("/login");
  };

  const handleLogin = () => {
    setIsLoggedIn(true);
    Cookies.set("access_token", "your_access_token", { expires: 1 });
    router.push("/");
  };

  // Handle dropdown toggle for mobile with single click
  const handleDropdownToggle = (setter, current) => {
    setter(!current);
  };

  if (!isMounted) {
    return null;
  }

  return (
    <nav className={styles.nav}>
      <div className={styles.alwaysVisible}>
        <Link href="/">Home</Link>
        <Link href="/expected-value">Expected Value</Link>
      </div>

      <div
        className={styles.hamburger}
        onClick={() => setIsMenuOpen(!isMenuOpen)}
      >
        <span></span>
        <span></span>
        <span></span>
      </div>

      <ul className={`${styles.navList} ${isMenuOpen ? styles.open : ""}`}>
        <li className={styles.navItem}>
          <Link href="/">Home</Link>
        </li>
        <li className={styles.navItem}>
          <Link href="/expected-value">Expected Value</Link>
        </li>

        {/* NFL Dropdown */}
        <li
          className={styles.navItem}
          onMouseEnter={() => setShowDropdown(true)}
          onMouseLeave={() => setShowDropdown(false)}
          onClick={(e) => {
            e.stopPropagation();
            handleDropdownToggle(setShowDropdown, showDropdown);
          }}
        >
          <span className={styles.navLink}>NFL</span>
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
          onClick={(e) => {
            e.stopPropagation();
            handleDropdownToggle(setShowDropdownNHL, showDropdownNHL);
          }}
        >
          <span className={styles.navLink}>NHL</span>
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
          onClick={(e) => {
            e.stopPropagation();
            handleDropdownToggle(setShowDropdownMLB, showDropdownMLB);
          }}
        >
          <span className={styles.navLink}>MLB</span>
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
          onClick={(e) => {
            e.stopPropagation();
            handleDropdownToggle(setShowDropdownNBA, showDropdownNBA);
          }}
        >
          <span className={styles.navLink}>NBA</span>
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

        {/* Arbitrage Dropdown */}
        <li
          className={styles.navItem}
          onMouseEnter={() => setShowDropdownArbitrage(true)}
          onMouseLeave={() => setShowDropdownArbitrage(false)}
          onClick={(e) => {
            e.stopPropagation();
            handleDropdownToggle(
              setShowDropdownArbitrage,
              showDropdownArbitrage
            );
          }}
        >
          <span className={styles.navLink}>Arbitrage</span>
          {showDropdownArbitrage && (
            <ul className={styles.dropdown}>
              <li>
                <Link href="/arbitrage">Opportunities</Link>
              </li>
              <li>
                <Link href="/arbitrage-opportunities">Tracking</Link>
              </li>
            </ul>
          )}
        </li>

        {isLoggedIn ? (
          <>
            <li className={`${styles.navItem} ${styles.rightAlign}`}>
              <Link href="/checkout">Subscribe</Link>
            </li>
            <li className={styles.navItem}>
              <Link href="/account">Account</Link>
            </li>
            <li className={styles.navItem}>
              <Link href="/" onClick={handleLogout}>
                Logout
              </Link>
            </li>
          </>
        ) : (
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
