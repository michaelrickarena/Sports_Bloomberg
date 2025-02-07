// Utility functions to manage JWT tokens and handle token refresh
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api";

// Check if the token is expired
export const isTokenExpired = (token) => {
  if (!token) return true;

  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  } catch (error) {
    console.error("Invalid token format", error);
    return true;
  }
};

// Refresh the access token using the refresh token
export const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) {
    console.warn("No refresh token available.");
    return null;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/token/refresh/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (response.ok) {
      const data = await response.json();
      if (data.access) {
        localStorage.setItem("access_token", data.access); // Save the new access token
        console.log("Access token successfully refreshed.");
        return data.access;
      } else {
        console.warn("No access token in the response.");
      }
    } else {
      console.error("Failed to refresh access token. Status:", response.status);
    }
  } catch (error) {
    console.error("Error refreshing access token:", error);
  }
  return null;
};

// Get a valid access token (refresh it if expired)
export const getValidAccessToken = async () => {
  let accessToken = localStorage.getItem("access_token");

  if (isTokenExpired(accessToken)) {
    console.log("Access token expired. Attempting to refresh...");
    accessToken = await refreshAccessToken();
  }

  return accessToken;
};
