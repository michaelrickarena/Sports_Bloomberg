"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ClipLoader } from "react-spinners"; // Import ClipLoader
import "../styles/login.css";

const PasswordResetRequest = () => {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false); // Add loading state
  const router = useRouter();

  const handleResetRequest = async (event) => {
    event.preventDefault();
    setLoading(true); // Set loading to true when the request starts
    setError(""); // Clear previous errors
    setMessage(""); // Clear previous messages

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/reset-password/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email }),
        }
      );

      const data = await response.json();
      if (response.ok) {
        setMessage("Password reset email sent. Please check your inbox.");
        setEmail("");
      } else {
        setError(data.detail || "Error sending password reset email.");
      }
    } catch (error) {
      setError("An error occurred. Please try again later.");
    } finally {
      setLoading(false); // Set loading to false when the request completes
    }
  };

  // Show ClipLoader while loading
  if (loading) {
    return (
      <div style={{ textAlign: "center", marginTop: "20px" }}>
        <ClipLoader size={100} color="#007bff" />
        <p>Sending reset link...</p>
      </div>
    );
  }

  return (
    <div>
      <h3>Forgot your password?</h3>
      <form onSubmit={handleResetRequest} className="form-container">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          required
          className="input-field"
        />
        {error && <p className="error-message">{error}</p>}
        {message && <p className="success-message">{message}</p>}
        <button type="submit" className="submit-button" disabled={loading}>
          Send Password Reset Link
        </button>
      </form>
    </div>
  );
};

export default PasswordResetRequest;
