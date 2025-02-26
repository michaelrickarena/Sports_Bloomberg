"use client";

import { useState, useEffect } from "react";

// Function to get access token from cookies
const getAccessToken = () => {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith("access_token="))
    ?.split("=")[1];
};

const CancelSubscription = () => {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [expirationDate, setExpirationDate] = useState(null);

  // Fetch subscription details on mount
  useEffect(() => {
    const fetchSubscriptionDetails = async () => {
      const accessToken = getAccessToken();
      if (!accessToken) {
        console.error("No access token found");
        return;
      }

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/subscription-details/`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
            credentials: "include",
          }
        );

        const data = await response.json();

        if (response.ok && data.expiration_date) {
          setExpirationDate(data.expiration_date);
        } else {
          setExpirationDate("No active subscription");
        }
      } catch (error) {
        console.error("Failed to fetch subscription details", error);
        setExpirationDate("Error fetching subscription details");
      }
    };

    fetchSubscriptionDetails();
  }, []);

  const handleCancelSubscription = async () => {
    setLoading(true);
    setMessage("");

    const accessToken = getAccessToken(); // Get token from cookies

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/cancel-subscription/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`, // Attach token
          },
          credentials: "include", // Still send cookies
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage("Your subscription has been scheduled for cancellation.");
      } else {
        setMessage(data.error || "Failed to cancel subscription.");
      }
    } catch (error) {
      setMessage("An error occurred. Please try again.");
    }

    setLoading(false);
  };

  return (
    <div>
      <p>
        Your subscription expires on: <b>{expirationDate || "Loading..."}</b>
      </p>
      <button
        onClick={handleCancelSubscription}
        disabled={loading}
        className="cancel-button"
      >
        {loading ? "Cancelling..." : "Cancel Subscription"}
      </button>
      {message && <p>{message}</p>}
    </div>
  );
};

export default CancelSubscription;
