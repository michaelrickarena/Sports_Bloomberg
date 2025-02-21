"use client";

import { useEffect, useState, useCallback } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { Elements } from "@stripe/react-stripe-js";
import { useRouter } from "next/navigation";

// Load Stripe public key
const stripePromise = loadStripe(
  "pk_test_51QmeHYB70pdVZrmYS3duPwmVq1zh0ziwd7Pa4BQk4Z7e3XYNwuSm9k419guRPAek1F2fp1RjXVKb4H47NDYNIXVK00iQrofFn9"
);

// Helper functions to manage cookies
const setCookie = (name, value, days) => {
  let expires = "";
  if (days) {
    const date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    expires = `; expires=${date.toUTCString()}`;
  }
  // Removed HttpOnly since it cannot be set from JavaScript
  document.cookie = `${name}=${value}; path=/${expires}`;
};

const getCookie = (name) => {
  const cookies = document.cookie.split("; ");
  for (const cookie of cookies) {
    const [cookieName, cookieValue] = cookie.split("=");
    if (cookieName === name) {
      return cookieValue;
    }
  }
  return null;
};

const deleteCookie = (name) => {
  document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;`;
};

const CheckoutForm = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSubscribed, setIsSubscribed] = useState(true);
  const [accessToken, setAccessToken] = useState(null);
  const router = useRouter();

  // On mount, load the access token from cookies
  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedAccessToken = getCookie("access_token");
      if (storedAccessToken) {
        setAccessToken(storedAccessToken);
      }
    }
  }, []);

  // Refresh the access token and return it for immediate use
  const refreshAccessToken = useCallback(async () => {
    const storedRefreshToken = getCookie("refresh_token");
    if (!storedRefreshToken) {
      console.error("No refresh token available. User may not be logged in.");
      setError("User not authenticated. Please log in.");
      return null;
    }
    try {
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

      if (!response.ok) {
        throw new Error("Failed to refresh access token.");
      }

      const data = await response.json();
      if (data.access) {
        setCookie("access_token", data.access, 1); // Store new access token
        setAccessToken(data.access);
        return data.access;
      } else {
        throw new Error("Refresh token is invalid or expired.");
      }
    } catch (error) {
      setError("Error refreshing access token.");
      console.error(error);
      return null;
    }
  }, []);

  // Check subscription status, refreshing token if necessary
  useEffect(() => {
    const checkSubscription = async () => {
      try {
        let token = accessToken;

        if (!token) {
          token = await refreshAccessToken();
          if (!token) {
            throw new Error("Authentication token is still missing.");
          }
        }

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
          token = await refreshAccessToken();
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

  // Handle Stripe checkout session creation and redirection
  const handleCheckout = async () => {
    if (!isSubscribed) {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/create-checkout-session/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify({}),
          }
        );

        if (!response.ok) {
          throw new Error(
            `Failed to create checkout session: ${response.status}`
          );
        }

        const session = await response.json();

        if (session.error) {
          throw new Error(`Error in session response: ${session.error}`);
        }

        const stripe = await stripePromise;
        if (!stripe) {
          throw new Error("Stripe has not loaded yet.");
        }

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
