"use client";

import { useState } from "react";

const CancelSubscription = () => {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleCancelSubscription = async () => {
    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/cancel-subscription/`, // Ensure correct API route
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include", // Send cookies automatically
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
