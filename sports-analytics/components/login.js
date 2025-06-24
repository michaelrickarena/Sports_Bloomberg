"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie"; // New import added
import "../styles/login.css";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = async (event) => {
    event.preventDefault();

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

      const data = await response.json();

      if (response.ok) {
        // Set access and refresh tokens as cookies - Original kept, modified to use js-cookie
        // document.cookie = `access_token=${data.access}; path=/; secure=true; samesite=None;`; // Original commented
        // document.cookie = `refresh_token=${data.refresh}; path=/; secure=true; samesite=None;`; // Original commented
        Cookies.set("access_token", data.access, {
          path: "/",
          secure: true,
          sameSite: "None",
        }); // New: Use js-cookie
        Cookies.set("refresh_token", data.refresh, {
          path: "/",
          secure: true,
          sameSite: "None",
        }); // New: Use js-cookie

        // Store exact subscription status in localStorage - Original kept
        if (data.subscription_active !== undefined) {
          localStorage.setItem("subscription_status", data.subscription_active);
          console.log(
            `[LOGIN COMPONENT] Subscription status saved: ${data.subscription_active}`
          );
        } else {
          console.log();
        }

        // Redirect to homepage - Original kept
        router.push("/");
        // refresh for styles
        setTimeout(() => {
          window.location.reload();
        }, 100);
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
      <h3 className="welcome">Welcome to the Login Page</h3>
      <p className="welcome-text">
        Logging in and having an active subscription is required to use this
        software.
      </p>
      <form onSubmit={handleLogin} className="login-form-container">
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
