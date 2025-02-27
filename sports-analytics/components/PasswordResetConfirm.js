"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation"; // Import from next/navigation
import "../styles/login.css";

const PasswordResetConfirm = () => {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [uidb64, setUidb64] = useState(null);
  const [token, setToken] = useState(null);

  const params = useParams(); // Get dynamic route parameters
  const router = useRouter(); // For navigation (e.g., router.push)

  // Set uidb64 and token from params when they’re available
  useEffect(() => {
    if (params?.uidb64 && params?.token) {
      setUidb64(params.uidb64);
      setToken(params.token);
    }
  }, [params]);

  const handlePasswordReset = async (event) => {
    event.preventDefault();

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (!uidb64 || !token) {
      setError("Invalid reset link.");
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/reset-password/${uidb64}/${token}/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ password }),
        }
      );

      const data = await response.json();
      if (response.ok) {
        setSuccess("Your password has been reset successfully.");
        setTimeout(() => router.push("/login"), 2000);
      } else {
        setError(data.detail || "Error resetting password.");
      }
    } catch (error) {
      setError("An error occurred. Please try again later.");
    }
  };

  // Show loading state until uidb64 and token are available
  if (!uidb64 || !token) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h3>Reset your password</h3>
      <form onSubmit={handlePasswordReset} className="form-container">
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="New password"
          required
          className="input-field"
        />
        <input
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="Confirm new password"
          required
          className="input-field"
        />
        {error && <p className="error-message">{error}</p>}
        {success && <p className="success-message">{success}</p>}
        <button type="submit" className="submit-button">
          Reset Password
        </button>
      </form>
    </div>
  );
};

export default PasswordResetConfirm;
