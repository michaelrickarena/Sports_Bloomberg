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
        <h1>Welcome to the Sports Analytics Website</h1>
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
