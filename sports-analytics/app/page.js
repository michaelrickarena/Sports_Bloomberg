"use client";

import Head from "next/head";
import "bootstrap/dist/css/bootstrap.min.css";
import { useState, useEffect } from "react";

export default function HomePage() {
  // Disclaimer logic (if needed)
  const [showDisclaimer, setShowDisclaimer] = useState(false);

  useEffect(() => {
    const disclaimerAccepted = localStorage.getItem("disclaimerAccepted");
    if (!disclaimerAccepted) {
      setShowDisclaimer(true);
    }
  }, []);

  const handleAcceptDisclaimer = () => {
    localStorage.setItem("disclaimerAccepted", "true");
    setShowDisclaimer(false);
  };

  return (
    <>
      <Head>
        <title>TheSmartLines | Sports Analytics Subscription</title>
        <meta
          name="description"
          content="Access arbitrage tracking, +EV bets, and detailed line graphs—all for $10/month."
        />
        {/* Bootstrap Icons */}
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
        />
      </Head>

      {/* Disclaimer Modal (if applicable) */}
      {showDisclaimer && (
        <div
          className="modal show d-block"
          tabIndex="-1"
          style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
        >
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Disclaimer</h5>
              </div>
              <div className="modal-body">
                <p>
                  This website is intended for informational purposes only.
                  Please ensure your betting activities comply with local laws.
                  Gamble responsibly.
                </p>
              </div>
              <div className="modal-footer">
                <button
                  onClick={handleAcceptDisclaimer}
                  className="btn btn-primary"
                >
                  I Understand
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <header
        className="masthead"
        style={{
          backgroundColor: "#343a40",
          color: "#fff",
          paddingTop: "120px",
          paddingBottom: "120px",
          textAlign: "center",
        }}
      >
        <div className="container">
          <h1 className="masthead-heading text-uppercase">
            Welcome to TheSmartLines
          </h1>
          <p className="masthead-subheading fw-light mb-0">
            Your Ultimate Sports Analytics Hub
          </p>
          <a
            className="btn btn-primary btn-xl text-uppercase mt-4"
            href="/register"
            role="button"
          >
            Start Free Trial
          </a>
        </div>
      </header>

      {/* Features Section */}
      <section id="features" style={{ padding: "60px 0" }}>
        <div className="container">
          <div className="row text-center">
            {/* Arbitrage Tracking / Alerts */}
            <div className="col-md-4 mb-5">
              <div className="feature-box">
                <i
                  className="bi bi-lightning-charge"
                  style={{ fontSize: "3rem", color: "#6c757d" }}
                ></i>
                <h3 className="my-3">Arbitrage Alerts</h3>
                <p className="text-muted">
                  Get real-time notifications for arbitrage opportunities to
                  secure risk-free profits.
                </p>
              </div>
            </div>
            {/* +EV Bets */}
            <div className="col-md-4 mb-5">
              <div className="feature-box">
                <i
                  className="bi bi-graph-up"
                  style={{ fontSize: "3rem", color: "#6c757d" }}
                ></i>
                <h3 className="my-3">+EV Bets</h3>
                <p className="text-muted">
                  Identify positive expected value bets to boost your edge.
                </p>
              </div>
            </div>
            {/* Graph Lines */}
            <div className="col-md-4 mb-5">
              <div className="feature-box">
                <i
                  className="bi bi-bar-chart-line"
                  style={{ fontSize: "3rem", color: "#6c757d" }}
                ></i>
                <h3 className="my-3">Graph Lines</h3>
                <p className="text-muted">
                  Explore interactive graphs to track betting line trends over
                  time.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section
        id="pricing"
        style={{ backgroundColor: "#f8f9fa", padding: "60px 0" }}
      >
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-lg-6">
              <div className="card text-center shadow-sm">
                <div className="card-body">
                  <h2 className="card-title">Subscription Plan</h2>
                  <p className="card-text">
                    Unlock full access to arbitrage tracking, +EV bets, and
                    detailed line graphs.
                  </p>
                  <h3 className="display-4">
                    $10<span className="small">/month</span>
                  </h3>
                  <a href="/register" className="btn btn-dark btn-lg mt-3">
                    Start Free Trial
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer / Contact */}
      <footer
        id="contact"
        style={{
          backgroundColor: "#343a40",
          color: "#fff",
          padding: "20px 0",
          textAlign: "center",
        }}
      >
        <div className="container">
          <p className="mb-0">
            &copy; {new Date().getFullYear()} TheSmartLines. All rights
            reserved.
          </p>
        </div>
      </footer>
    </>
  );
}
