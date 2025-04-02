"use client";

import { useState } from "react";
import Link from "next/link";
import "../styles/login.css";
import ClipLoader from "react-spinners/ClipLoader";

const Register = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleRegister = async (event) => {
    event.preventDefault();

    if (!termsAccepted) {
      alert("You must agree to the terms and conditions.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/register_and_get_jwt/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: username,
            password: password,
            email: email,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        alert(
          "Please check your email to verify your account before logging in."
        );
        window.location.href = "/login"; // Redirect to login page instead of logging in immediately
      } else {
        console.error("Registration failed:", data);
        alert(data.error || "Registration failed. Please try again.");
        setLoading(false);
      }
    } catch (error) {
      console.error("Error during registration:", error);
      alert("An error occurred. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div>
      <h3 className="Free-Trial-Title">7 Day Free Trial</h3>
      <p className="Free-Trial-text">
        For a short period of time, all new accounts will be given a free trial.
      </p>
      <form className="login-form-container" onSubmit={handleRegister}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          required
          className="input-field"
        />
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
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
        <div className="terms-container" style={{ margin: "1rem 0" }}>
          <input
            type="checkbox"
            id="terms"
            required
            checked={termsAccepted}
            onChange={(e) => setTermsAccepted(e.target.checked)}
          />
          <label htmlFor="terms" style={{ marginLeft: "0.5rem" }}>
            I have read and agree to the{" "}
            <Link href="/termsandconditions">Terms and Conditions</Link>
          </label>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? <ClipLoader size={20} color="#ffff" /> : "Register"}
        </button>
      </form>
    </div>
  );
};

export default Register;
