"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { usePathname } from "next/navigation";
import Cookies from "js-cookie";
import Image from "next/image";
import styles from "../styles/NavBar.module.css";

const NavBar = () => {
  const router = useRouter();
  const pathname = usePathname();
  const [showDropdown, setShowDropdown] = useState(false);
  const [showDropdownNHL, setShowDropdownNHL] = useState(false);
  const [showDropdownMLB, setShowDropdownMLB] = useState(false);
  const [showDropdownNBA, setShowDropdownNBA] = useState(false);
  const [showDropdownArbitrage, setShowDropdownArbitrage] = useState(false);
  const [showDropdownCalculators, setShowDropdownCalculators] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const token = Cookies.get("access_token");
    setIsLoggedIn(!!token);
  }, [pathname]);

  useEffect(() => {
    setIsMenuOpen(false);
    setShowDropdown(false);
    setShowDropdownNHL(false);
    setShowDropdownMLB(false);
    setShowDropdownNBA(false);
    setShowDropdownArbitrage(false);
    setShowDropdownCalculators(false);
  }, [pathname]);

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

  return (
    <nav className={styles.nav + " flex items-center"}>
      {/* Always visible: Logo and Home */}
      <div className="flex items-center gap-2 pl-2 py-1">
        <Link href="/">
          <Image
            src="/assets/images/logo-big.png"
            alt="Logo-big"
            width={175}
            height={175}
            className="inline-block align-middle rounded-md"
            priority
          />
        </Link>
        <Link href="/" className="ml-2 mr-4">
          Home
        </Link>
      </div>
      {/* Hamburger for mobile */}
      <div
        className={styles.hamburger}
        onClick={() => setIsMenuOpen(!isMenuOpen)}
      >
        <span></span>
        <span></span>
        <span></span>
      </div>
      {/* Nav list: all nav items except Home, hidden on mobile unless hamburger is open */}
      <ul
        className={`${styles.navList} ${isMenuOpen ? styles.open : ""}`}
        style={{ width: "100%" }}
      >
        {/* Expected Value */}
        <li className={styles.navItem}>
          <Link href="/expected-value">Expected Value</Link>
        </li>
        {/* NFL Dropdown */}
        <li
          className={styles.navItem}
          onMouseEnter={!isMenuOpen ? () => setShowDropdown(true) : undefined}
          onMouseLeave={!isMenuOpen ? () => setShowDropdown(false) : undefined}
          onClick={
            isMenuOpen
              ? (e) => {
                  e.stopPropagation();
                  handleDropdownToggle(setShowDropdown, showDropdown);
                }
              : undefined
          }
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
          onMouseEnter={
            !isMenuOpen ? () => setShowDropdownNHL(true) : undefined
          }
          onMouseLeave={
            !isMenuOpen ? () => setShowDropdownNHL(false) : undefined
          }
          onClick={
            isMenuOpen
              ? (e) => {
                  e.stopPropagation();
                  handleDropdownToggle(setShowDropdownNHL, showDropdownNHL);
                }
              : undefined
          }
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
          onMouseEnter={
            !isMenuOpen ? () => setShowDropdownMLB(true) : undefined
          }
          onMouseLeave={
            !isMenuOpen ? () => setShowDropdownMLB(false) : undefined
          }
          onClick={
            isMenuOpen
              ? (e) => {
                  e.stopPropagation();
                  handleDropdownToggle(setShowDropdownMLB, showDropdownMLB);
                }
              : undefined
          }
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
          onMouseEnter={
            !isMenuOpen ? () => setShowDropdownNBA(true) : undefined
          }
          onMouseLeave={
            !isMenuOpen ? () => setShowDropdownNBA(false) : undefined
          }
          onClick={
            isMenuOpen
              ? (e) => {
                  e.stopPropagation();
                  handleDropdownToggle(setShowDropdownNBA, showDropdownNBA);
                }
              : undefined
          }
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
          onMouseEnter={
            !isMenuOpen ? () => setShowDropdownArbitrage(true) : undefined
          }
          onMouseLeave={
            !isMenuOpen ? () => setShowDropdownArbitrage(false) : undefined
          }
          onClick={
            isMenuOpen
              ? (e) => {
                  e.stopPropagation();
                  handleDropdownToggle(
                    setShowDropdownArbitrage,
                    showDropdownArbitrage
                  );
                }
              : undefined
          }
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

        {/* Calculators Dropdown */}
        <li
          className={styles.navItem}
          onMouseEnter={
            !isMenuOpen ? () => setShowDropdownCalculators(true) : undefined
          }
          onMouseLeave={
            !isMenuOpen ? () => setShowDropdownCalculators(false) : undefined
          }
          onClick={
            isMenuOpen
              ? (e) => {
                  e.stopPropagation();
                  handleDropdownToggle(
                    setShowDropdownCalculators,
                    showDropdownCalculators
                  );
                }
              : undefined
          }
        >
          <span className={styles.navLink}>Calculators</span>
          {showDropdownCalculators && (
            <ul className={styles.dropdown}>
              <li>
                <Link href="/calculators/arbitrage">Arbitrage</Link>
              </li>
              <li>
                <Link href="/calculators/expected-value">Expected Value</Link>
              </li>
              <li>
                <Link href="/calculators/hedge">Hedge</Link>
              </li>
              <li>
                <Link href="/calculators/implied-odds">Implied Odds</Link>
              </li>
              <li>
                <Link href="/calculators/kelly-criterion">Kelly Criterion</Link>
              </li>
              <li>
                <Link href="/calculators/no-vig">No Vig</Link>
              </li>
              <li>
                <Link href="/calculators/odds-conversion">Odds Conversion</Link>
              </li>
              <li>
                <Link href="/calculators/parlay">Parlay</Link>
              </li>
            </ul>
          )}
        </li>

        {/* Blogs Nav Item (no dropdown) */}
        <li className={styles.navItem}>
          <Link href="/blogs" className={styles.navLink}>
            Blogs
          </Link>
        </li>

        {/* Account/Login actions inside navList, rightAlign on first item */}
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
