"use client";

import { useState, useEffect } from "react";

export default function VerifyEmailComponent() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const uid = urlParams.get("uid");
    const token = urlParams.get("token");

    if (uid && token) {
      // Debugging: Log the body of the fetch request
      const requestBody = { uid, token };

      fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/verify-email/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody), // Send both uid and token in the request body
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.message) {
            setStatus("success");
          } else {
            setStatus("failure");
          }
        })
        .catch((err) => {
          setStatus("error");
        });
    }
  }, []);

  if (status === "success") {
    return <div>Email verified successfully!</div>;
  }

  if (status === "failure") {
    return <div>Verification failed. Please try again.</div>;
  }

  return <div>Verifying...</div>;
}
