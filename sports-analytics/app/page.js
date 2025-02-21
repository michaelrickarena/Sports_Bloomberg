"use client";

// app/page.js (Root/Home Page)
import React, { useState, useEffect } from "react"; // Add useEffect here
import Link from "next/link";
import styles from "../styles/HomePage.module.css"; // Import the CSS module

const HomePage = () => {
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);

  useEffect(() => {
    const accepted = localStorage.getItem("disclaimerAccepted");
    if (accepted) {
      setDisclaimerAccepted(true);
    }
  }, []);

  const handleAccept = () => {
    setDisclaimerAccepted(true);
    localStorage.setItem("disclaimerAccepted", "true");
  };

  if (disclaimerAccepted) {
    return (
      <div>
        <h1 className={styles.title}>
          Welcome to TheSmartLines.ca – Your Ultimate Sports Analytics Hub!
        </h1>

        <section>
          <p className={styles.firstpara}>
            At SmartLines, we empower your sports betting experience with
            advanced data analytics and actionable insights—all at an affordable
            price. Our mission is to equip everyday bettors with the same
            sophisticated analysis used by the pros, so you can pinpoint the
            best bookmakers and the optimal moments to place your bets by
            tracking market trends and the influence of sharp money on betting
            lines. Very soon we will introduce our new arbitrage monitoring
            feature. This functionality allows you to log your active bets and
            receive real-time notifications when an arbitrage opportunity
            arises—matched to the return threshold you set. Whether you’re a
            seasoned bettor or just starting out, SmartLines provides
            comprehensive data on <strong>Moneylines</strong>,{" "}
            <strong>Spreads</strong>, <strong>Over/Unders</strong>, and{" "}
            <strong>Player Props</strong> for the NFL, NBA, MLB, and NHL, with
            plans to expand into even more sports. Let SmartLines be your guide
            to smarter, more strategic betting.
          </p>

          <h3>How It Works</h3>

          <div className={styles.gridContainer}>
            <div className={styles.gridItem}>
              <h3>Moneyline</h3>
              <p>
                The Moneyline is one of the most straightforward betting
                options. It simply reflects the odds for a team to win. If you
                bet on the Moneyline, you’re picking which team will win
                outright, with no need to worry about the point spread. We
                provide you with up-to-date and historical Moneyline odds from
                various bookies, helping you identify the best value and
                opportunities for profitable bets. Our graphs are currently used
                for trend and technical analysis
              </p>
            </div>

            <div className={styles.gridItem}>
              <h3>Spread</h3>
              <p>
                In spread betting, the favorite team must win by a certain
                number of points, while the underdog team can lose by fewer
                points (or win outright) for your bet to be successful. Our{" "}
                <strong>spread</strong> section breaks down the odds and
                provides you with key insights into the spread for each game,
                allowing you to compare line movements and spot favorable
                opportunities.
              </p>
            </div>

            <div className={styles.gridItem}>
              <h3>Over/Under</h3>
              <p>
                The Over/Under, also known as the Total, is a bet on the total
                combined points (or other statistical metrics) of both teams in
                a game. Our <strong>Over/Under</strong> section keeps track of
                all available totals for each game and displays the current
                odds, helping you evaluate how both teams are performing and if
                the projected total is a good betting opportunity.
              </p>
            </div>

            <div className={styles.gridItem}>
              <h3>Player Props</h3>
              <p>
                Player Prop bets are a fun and unique way to engage with the
                game by betting on individual player performances. Whether it’s
                the total passing yards of a quarterback, the number of points
                scored by a basketball player, or how many strikeouts a pitcher
                will have, our <strong>Player Props</strong> section gives you
                all the data you need to make informed decisions on
                player-specific bets.
              </p>
            </div>
          </div>

          <h3>Why Choose Us?</h3>

          <div className={styles.gridContainer}>
            <div className={styles.gridItem}>
              <h3>Comprehensive Coverage</h3>

              <p>
                We cover a wide range of sports and betting markets, so you can
                find data on all your favorite teams and players.
              </p>
            </div>
            <div className={styles.gridItem}>
              <h3>Up-to-date Odds</h3>
              <p>
                Our platform updates odds and statistics in real-time, giving
                you the edge in your betting decisions.
              </p>
            </div>
            <div className={styles.gridItem}>
              <h3>User-friendly Interface</h3>
              <p>
                Easily navigate between different sports, games, and bet types
                with our intuitive interface.
              </p>
            </div>
            <div className={styles.gridItem}>
              <h3>Arbitrage Opportunities</h3>
              <p>
                We help you identify discrepancies between bookies, giving you
                the chance to take advantage of arbitrage opportunities for
                risk-free profits.
              </p>
            </div>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div>
      <div className={styles.modal}>
        <div className={styles.modalContent}>
          <h2>DISCLAIMER</h2>
          <p>
            By using this website, you agree to the following terms and
            conditions:
          </p>

          <h2>No Responsibility for Betting Risks:</h2>
          <p>
            This website and its contents are provided for informational
            purposes only. We do not take any responsibility for any actions you
            take based on the information presented on this site, including but
            not limited to, any betting decisions, wagers, or financial
            transactions. All betting activities carry inherent risks, and we
            strongly advise that you exercise caution and consider all risks
            before engaging in any betting activities.
          </p>

          <h2>Accuracy of Information:</h2>
          <p>
            While we strive to provide accurate and up-to-date data, we do not
            guarantee the completeness, accuracy, or reliability of any
            information presented on this website. The data and content are
            subject to change without notice. We do not assume any liability for
            errors or omissions, and users of this website should independently
            verify any information before making any decisions.
          </p>

          <h2>Not a Betting Service:</h2>
          <p>
            This website does not provide betting services, nor do we facilitate
            any form of gambling. We are not responsible for any financial
            losses, legal issues, or disputes arising from the use of this site,
            or from any bets or wagers placed on third-party platforms.
          </p>

          <h2>Legal Compliance:</h2>
          <p>
            It is your responsibility to ensure that any betting activity you
            engage in is compliant with the laws and regulations of your
            jurisdiction. We do not advocate or encourage illegal gambling or
            activities that violate any local, state, or national laws. By
            accessing this site, you acknowledge that you are doing so in
            accordance with the laws of your location.
          </p>

          <h2>Limitation of Liability:</h2>
          <p>
            To the fullest extent permitted by law, we disclaim any and all
            liability for any direct, indirect, incidental, special,
            consequential, or punitive damages arising from the use or inability
            to use this website, including any errors in the content or
            interruptions in the service. This includes, without limitation, any
            loss of data, loss of profit, or any other loss incurred through the
            use of this site.
          </p>

          <h2>No Financial Advice:</h2>
          <p>
            The content on this website does not constitute financial, legal, or
            betting advice. Any opinions or views expressed are solely those of
            the authors and do not represent the views of any other parties or
            organizations.
          </p>

          <h2>Changes to Disclaimer:</h2>
          <p>
            We reserve the right to modify or update this disclaimer at any time
            without prior notice. By continuing to use this website, you agree
            to be bound by the revised terms and conditions.
          </p>
          <button className={styles.acceptButton} onClick={handleAccept}>
            Accept
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
