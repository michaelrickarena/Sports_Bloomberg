"use client"; // Add this line at the top of the file to mark this component as a client component

import { useState } from "react";
import "../styles/login.css"; // Import the CSS file without assigning it to a variable

const Register = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState(""); // New state for email

  const handleRegister = async (event) => {
    event.preventDefault();

    const response = await fetch(
      "http://127.0.0.1:8000/api/register_and_get_jwt/",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          password: password,
          email: email, // Include the email in the request body
        }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      // Save the token in localStorage
      localStorage.setItem("access_token", data.access);

      // Redirect to the homepage or dashboard
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
