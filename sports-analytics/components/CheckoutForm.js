import { useEffect, useState } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { Elements } from "@stripe/react-stripe-js";
import { useRouter } from "next/router";

// Load Stripe public key
const stripePromise = loadStripe(
  "pk_test_51QmeHYB70pdVZrmYS3duPwmVq1zh0ziwd7Pa4BQk4Z7e3XYNwuSm9k419guRPAek1F2fp1RjXVKb4H47NDYNIXVK00iQrofFn9"
);

const CheckoutForm = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSubscribed, setIsSubscribed] = useState(true); // Track subscription status
  const router = useRouter();

  useEffect(() => {
    const checkSubscription = async () => {
      try {
        // Fetch subscription status from the backend
        const response = await fetch("/api/check-subscription");
        if (!response.ok) {
          throw new Error("Error fetching subscription status.");
        }

        const data = await response.json();

        // If subscription is inactive or trial expired, show checkout
        if (data.status === "inactive" || data.status === "expired") {
          setIsSubscribed(false);
        }
      } catch (error) {
        setError("Error checking subscription.");
        console.error(error);
      }
    };
    checkSubscription();
  }, []);

  const handleCheckout = async () => {
    if (!isSubscribed) {
      setLoading(true);
      setError(null); // Reset error state

      try {
        console.log("Initiating checkout...");

        const response = await fetch(
          "http://127.0.0.1:8000/create-checkout-session/",
          { method: "POST" }
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
