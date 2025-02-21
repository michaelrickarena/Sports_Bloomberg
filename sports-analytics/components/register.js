"use client";

import { useState } from "react";
import "../styles/login.css";

const Register = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");

  const setCookie = (name, value, days) => {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;Secure;SameSite=Strict`;
  };

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
      // Save access and refresh tokens as cookies
      setCookie("access_token", data.access, 1); // Expires in 1 day
      setCookie("refresh_token", data.refresh, 30); // Expires in 30 days

      // Redirect to homepage or dashboard
      window.location.href = "/";
    } else {
      console.error("Registration failed:", data);
    }
  };

  return (
    <form onSubmit={handleRegister}>
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
  );
};

export default Register;
