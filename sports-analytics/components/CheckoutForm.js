"use client";

import { useEffect, useState, useCallback } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { Elements } from "@stripe/react-stripe-js";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie"; // Import js-cookie

// Load Stripe public key
const stripePromise = loadStripe(
  "pk_test_51QmeHYB70pdVZrmYS3duPwmVq1zh0ziwd7Pa4BQk4Z7e3XYNwuSm9k419guRPAek1F2fp1RjXVKb4H47NDYNIXVK00iQrofFn9"
);

const CheckoutForm = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSubscribed, setIsSubscribed] = useState(true); // Track subscription status
  const [accessToken, setAccessToken] = useState(null); // Track the access token
  const [refreshToken, setRefreshToken] = useState(
    Cookies.get("refresh_token")
  ); // Get the refresh token from cookies
  const router = useRouter();

  // Function to refresh access token using the refresh token
  const refreshAccessToken = useCallback(async () => {
    try {
      console.log("Attempting to refresh access token...");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/token/refresh/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh: refreshToken }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to refresh access token.");
      }

      const data = await response.json();
      if (data.access) {
        Cookies.set("access_token", data.access); // Store new access token in cookies
        setAccessToken(data.access); // Update accessToken state
        console.log("Access token refreshed:", data.access);
      } else {
        throw new Error("Refresh token is invalid or expired.");
      }
    } catch (error) {
      setError("Error refreshing access token.");
      console.error(error);
    }
  }, [refreshToken]); // Add refreshToken to the dependency array to ensure it's updated

  useEffect(() => {
    const checkSubscription = async () => {
      try {
        let token = Cookies.get("access_token"); // Get the token from cookies
        console.log("Token retrieved from cookies:", token);

        // If there's no token, or it's expired, refresh the token
        if (!token) {
          console.log("Access token missing, refreshing token...");
          await refreshAccessToken();
          token = Cookies.get("access_token"); // Re-fetch the token after refreshing
        }

        // If there's still no token after refreshing, show error
        if (!token) {
          throw new Error("Authentication token is still missing.");
        }

        // Fetch subscription status from the backend with the token in the Authorization header
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/check-subscription`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`, // Send the updated token
            },
          }
        );

        if (response.status === 401) {
          console.log("Received 401 Unauthorized, refreshing token...");
          await refreshAccessToken(); // Attempt to refresh the token on 401
          token = Cookies.get("access_token"); // Fetch the new token

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
  }, [accessToken, refreshToken, refreshAccessToken]); // Add refreshAccessToken to dependencies

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
              // Add any necessary headers, such as Authorization for authenticated requests if needed
            },
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
