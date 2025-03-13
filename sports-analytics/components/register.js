"use client";

import { useState } from "react";
import "../styles/login.css";

const Register = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");

  const handleRegister = async (event) => {
    event.preventDefault();

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
    }
  };

  return (
    <div>
      <h2 className="Free-Trial-Title">7 Day Free Trial</h2>
      <p className="Free-Trial-text">
        {" "}
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
        <button type="submit">Register</button>
      </form>
    </div>
  );
};

export default Register;
