"use client";

import { useEffect, useState, useCallback } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { Elements } from "@stripe/react-stripe-js";
import { useRouter } from "next/navigation";

// Load Stripe public key
const stripePromise = loadStripe(
  "pk_test_51QmeHYB70pdVZrmYS3duPwmVq1zh0ziwd7Pa4BQk4Z7e3XYNwuSm9k419guRPAek1F2fp1RjXVKb4H47NDYNIXVK00iQrofFn9"
);

const CheckoutForm = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSubscribed, setIsSubscribed] = useState(true); // Track subscription status
  const [accessToken, setAccessToken] = useState(null); // Track the access token
  const router = useRouter();

  // On client mount, retrieve tokens from localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedAccessToken = localStorage.getItem("access_token");
      if (storedAccessToken) {
        setAccessToken(storedAccessToken);
      }
      // Note: We don't store the refresh token in state because we'll read it directly from localStorage
    }
  }, []);

  // Function to refresh access token using the refresh token from localStorage
  const refreshAccessToken = useCallback(async () => {
    const storedRefreshToken = localStorage.getItem("refresh_token");
    if (!storedRefreshToken) {
      console.error("No refresh token available. User may not be logged in.");
      setError("User not authenticated. Please log in.");
      return;
    }
    try {
      console.log(
        "Attempting to refresh access token with refresh token:",
        storedRefreshToken
      );
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/token/refresh/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh: storedRefreshToken }),
        }
      );
      console.log("Refresh token response status:", response.status);
      if (!response.ok) {
        const errorData = await response.text();
        console.error(
          "Failed to refresh access token. Response data:",
          errorData
        );
        throw new Error("Failed to refresh access token.");
      }
      const data = await response.json();
      if (data.access) {
        localStorage.setItem("access_token", data.access); // Store new access token in localStorage
        setAccessToken(data.access); // Update accessToken state
        console.log("Access token refreshed:", data.access);
      } else {
        console.error("Refresh token is invalid or expired.", data);
        throw new Error("Refresh token is invalid or expired.");
      }
    } catch (error) {
      setError("Error refreshing access token.");
      console.error(error);
    }
  }, []);

  useEffect(() => {
    const checkSubscription = async () => {
      try {
        let token = accessToken; // Use state for the token
        console.log("Token retrieved from state:", token);

        // If there's no token, attempt to refresh it
        if (!token) {
          console.log("Access token missing, attempting to refresh token...");
          await refreshAccessToken();
          token = localStorage.getItem("access_token"); // Re-fetch the token after refreshing
        }

        // If there's still no token after refreshing, throw an error
        if (!token) {
          throw new Error("Authentication token is still missing.");
        }

        // Fetch subscription status from the backend using the token
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/check-subscription`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.status === 401) {
          console.log("Received 401 Unauthorized, refreshing token...");
          await refreshAccessToken(); // Attempt to refresh the token on 401
          token = localStorage.getItem("access_token"); // Get the new token

          // Retry the subscription check after refreshing the token
          if (token) {
            const retryResponse = await fetch(
              `${process.env.NEXT_PUBLIC_API_BASE_URL}/check-subscription`,
              {
                method: "GET",
                headers: {
                  Authorization: `Bearer ${token}`,
                },
              }
            );

            if (!retryResponse.ok) {
              throw new Error(
                "Error fetching subscription status after retry."
              );
            }

            const data = await retryResponse.json();
            if (data.status === "inactive" || data.status === "expired") {
              setIsSubscribed(false);
            }
          } else {
            throw new Error("Token refresh failed or still invalid.");
          }
        } else if (response.ok) {
          const data = await response.json();
          // If subscription is inactive or trial expired, show checkout
          if (data.status === "inactive" || data.status === "expired") {
            setIsSubscribed(false);
          }
        } else {
          throw new Error("Error fetching subscription status.");
        }
      } catch (error) {
        setError("Error checking subscription.");
        console.error(error);
      }
    };

    checkSubscription();
  }, [accessToken, refreshAccessToken]);

  const handleCheckout = async () => {
    if (!isSubscribed) {
      setLoading(true);
      setError(null); // Reset error state

      try {
        console.log("Initiating checkout...");

        // Fetch session data for Stripe Checkout session
        const response = await fetch(
          "http://127.0.0.1:8000/create-checkout-session/",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify({}), // if needed
          }
        );

        if (!response.ok) {
          throw new Error(
            `Failed to create checkout session: ${response.status}`
          );
        }

        const session = await response.json();
        console.log("Session received from backend:", session);

        if (session.error) {
          throw new Error(`Error in session response: ${session.error}`);
        }

        const stripe = await stripePromise;
        if (!stripe) {
          throw new Error("Stripe has not loaded yet.");
        }

        // Redirect to Stripe Checkout
        const result = await stripe.redirectToCheckout({
          sessionId: session.id,
        });

        if (result.error) {
          throw new Error(
            `Error during redirect to checkout: ${result.error.message}`
          );
        }
      } catch (error) {
        setError(error.message);
        console.error(error.message);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div>
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {isSubscribed ? (
        <p>Your trial is still active or your subscription is valid!</p>
      ) : (
        <div>
          <p>
            Your trial has expired or your subscription is inactive. Please
            subscribe now.
          </p>
          <button role="link" onClick={handleCheckout} disabled={loading}>
            {loading ? "Loading..." : "Subscribe Now"}
          </button>
        </div>
      )}
    </div>
  );
};

const StripeCheckoutPage = () => {
  return (
    <Elements stripe={stripePromise}>
      <CheckoutForm />
    </Elements>
  );
};

export default StripeCheckoutPage;
