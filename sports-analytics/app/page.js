"use client";

import Head from "next/head";
import "bootstrap/dist/css/bootstrap.min.css";
import { useAuth } from "./contexts/AuthContext";

// Dummy auth check (replace with your actual auth logic) - Original kept
const useAuthDummy = () => {
  const isLoggedIn = false;
  return { isLoggedIn };
};

export default function HomePage() {
  const { isLoggedIn } = useAuth();
  console.log("HomePage isLoggedIn:", isLoggedIn);

  return (
    <>
      <Head>
        <title>TheSmartLines | Sports Analytics Subscription</title>
        <meta
          name="description"
          content="Unlock real-time arbitrage alerts, identify profitable +EV bets, and analyze betting trends with interactive graphs. All for just $10/month. Start your free trial today!"
        />
        <meta
          property="og:title"
          content="TheSmartLines | Sports Analytics Subscription"
        />
        <meta
          property="og:description"
          content="Unlock real-time arbitrage alerts, identify profitable +EV bets, and analyze betting trends with interactive graphs. All for just $10/month. Start your free trial today!"
        />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://www.thesmartlines.com/" />
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
        />
      </Head>

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
          <h5 className="masthead-subheading fw-light mb-0">
            Your Ultimate Sports Analytics Hub
          </h5>
          <a
            className="btn btn-primary btn-xl text-uppercase mt-4"
            href={isLoggedIn ? "/checkout" : "/register"} // Dynamic href
            role="button"
          >
            {isLoggedIn ? "Renew Your Subscription" : "Start Free Trial"}{" "}
            {/* Dynamic text */}
          </a>
        </div>
      </header>

      {/* Features Section */}
      <section id="features" style={{ padding: "60px 0" }}>
        <div className="container">
          <div className="row text-center">
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
                  <a
                    href={isLoggedIn ? "/checkout" : "/register"} // Dynamic href
                    className="btn btn-dark btn-lg mt-3"
                  >
                    {isLoggedIn
                      ? "Renew Your Subscription"
                      : "Start Free Trial"}{" "}
                    {/* Dynamic text */}
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
          <h5 className="masthead-subheading fw-light mb-0">
            © {new Date().getFullYear()} TheSmartLines. All rights reserved.
          </h5>
        </div>
      </footer>
    </>
  );
}
