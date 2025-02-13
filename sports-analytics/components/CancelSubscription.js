"use client";

import { useState, useEffect } from "react";

const CancelSubscription = () => {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState(null);

  useEffect(() => {
    // Retrieve JWT token from local storage (or cookies if stored there)
    const storedToken = localStorage.getItem("access_token");
    setToken(storedToken);
  }, []);

  const handleCancelSubscription = async () => {
    if (!token) {
      setMessage("You must be logged in to cancel your subscription.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/cancel-subscription/`, // Ensure correct API route
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`, // Include JWT in request headers
          },
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
      <h3>Manage Subscription</h3>
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
