"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import "../styles/login.css";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = async (event) => {
    event.preventDefault();

    console.log("[LOGIN COMPONENT] Attempting login...");
    console.log("[LOGIN COMPONENT] Username:", username);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/login/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, password }),
          credentials: "include", // Ensures cookies are included in the request
        }
      );

      console.log("[LOGIN COMPONENT] Server response status:", response.status);
      const data = await response.json();
      console.log("[LOGIN COMPONENT] Response data:", data);

      if (response.ok) {
        console.log("[LOGIN COMPONENT] Login successful, redirecting...");

        // Set access and refresh tokens as cookies
        document.cookie = `access_token=${data.access}; path=/; secure=true; samesite=None;`;
        document.cookie = `refresh_token=${data.refresh}; path=/; secure=true; samesite=None;`;

        // Store exact subscription status in localStorage
        if (data.subscription_active !== undefined) {
          localStorage.setItem("subscription_status", data.subscription_active);
          console.log(
            `[LOGIN COMPONENT] Subscription status saved: ${data.subscription_active}`
          );
        } else {
          console.log(
            "[LOGIN COMPONENT] No subscription status found in response."
          );
        }

        // Redirect to homepage
        router.push("/");
      } else {
        console.log("[LOGIN COMPONENT] Login failed:", data.detail);
        setError(
          data.detail ||
            "Login failed. Please check your credentials or verify your email."
        );
      }
    } catch (error) {
      setError("An error occurred. Please try again later.");
      console.error("[LOGIN COMPONENT] Login error:", error);
    }
  };

  return (
    <>
      <h3>Welcome to the Login Page</h3>
      <h4>
        Logging in and having an active subscription is required to use this
        software.
      </h4>
      <form onSubmit={handleLogin} className="form-container">
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username or Email"
          required
          className="input-field"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
          className="input-field"
        />
        {error && <p className="error-message">{error}</p>}

        {/* Forgot Password Link */}
        <div className="forgot-password-container">
          <a
            href="/password-reset/" // Directs user to the reset password request page
            className="forgot-password-link"
          >
            Forgot your password?
          </a>
        </div>

        <button type="submit" className="submit-button">
          Login
        </button>
      </form>
    </>
  );
};

export default Login;
