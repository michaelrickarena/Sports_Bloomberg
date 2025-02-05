"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = async (event) => {
    event.preventDefault();

    try {
      // Change the endpoint to the token endpoint in Django
      const response = await fetch("http://127.0.0.1:8000/api/token/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }), // Send the username and password to Django
      });

      const data = await response.json();

      if (response.ok) {
        // Save the JWT token in localStorage
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh); // Optionally save the refresh token

        // Redirect to the homepage or dashboard
        router.push("/"); // Change this to a different route if needed
      } else {
        setError(data.error || "Login failed. Please check your credentials.");
      }
    } catch (error) {
      setError("An error occurred. Please try again later.");
      console.error("Login error:", error);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      {error && <p style={{ color: "red" }}>{error}</p>}
      <button type="submit">Login</button>
    </form>
  );
};

export default Login;
