"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import "../styles/login.css"; // Import the CSS file without assigning it to a variable

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = async (event) => {
    event.preventDefault();

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/login/`, // Corrected this line
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, password }),
          credentials: "include", // Add this line to include cookies in the request
        }
      );
      const data = await response.json();

      if (response.ok && data.access && data.refresh) {
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);

        router.push("/");
      } else {
        setError(data.detail || "Login failed. Please check your credentials.");
      }
    } catch (error) {
      setError("An error occurred. Please try again later.");
      console.error("Login error:", error);
    }
  };

  return (
    <>
      <h3>Welcome to the Login Page</h3>
      <form onSubmit={handleLogin} className="form-container">
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
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
        <button type="submit" className="submit-button">
          Login
        </button>
      </form>
    </>
  );
};

export default Login;
