"use client";

import { createContext, useContext, useState, useEffect } from "react";
import Cookies from "js-cookie";
import { jwtDecode } from "jwt-decode";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [accessToken, setAccessToken] = useState(Cookies.get("access_token"));

  const checkAndRefreshToken = async () => {
    const currentAccessToken = Cookies.get("access_token");
    const refreshToken = Cookies.get("refresh_token");
    let isUserLoggedIn = !!currentAccessToken && !!refreshToken;
    let currentSubscriptionStatus = localStorage.getItem("subscription_status");

    console.log("Checking tokens:", { currentAccessToken, refreshToken });

    if (currentAccessToken) {
      try {
        const decodedToken = jwtDecode(currentAccessToken);
        const currentTime = Date.now() / 1000;

        console.log("Decoded token:", decodedToken);

        if (decodedToken.exp < currentTime && refreshToken) {
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_BASE_URL}/token/refresh-token`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ refreshToken }),
            }
          );

          if (response.ok) {
            const data = await response.json();
            Cookies.set("access_token", data.accessToken, {
              path: "/",
              secure: true,
              sameSite: "None",
            });
            setAccessToken(data.accessToken);
            const newDecodedToken = jwtDecode(data.accessToken);
            currentSubscriptionStatus =
              newDecodedToken.subscription_status || currentSubscriptionStatus;
            localStorage.setItem(
              "subscription_status",
              currentSubscriptionStatus
            );
            isUserLoggedIn = true;
          } else {
            isUserLoggedIn = false;
          }
        } else {
          currentSubscriptionStatus =
            decodedToken.subscription_status || currentSubscriptionStatus;
        }
      } catch (error) {
        console.error("Error processing token:", error);
        isUserLoggedIn = false;
      }
    } else {
      isUserLoggedIn = false;
    }

    console.log("Setting isLoggedIn:", isUserLoggedIn);
    setIsLoggedIn(isUserLoggedIn);
    setSubscriptionStatus(currentSubscriptionStatus);
    setIsLoading(false);
  };

  // Initial check on mount - Original kept
  useEffect(() => {
    checkAndRefreshToken();
  }, []);

  // Proactive token refresh - Original kept
  useEffect(() => {
    if (accessToken) {
      try {
        const decodedToken = jwtDecode(accessToken);
        const currentTime = Date.now() / 1000;
        if (decodedToken.exp > currentTime) {
          const expiresIn = (decodedToken.exp - currentTime) * 1000;
          const refreshTime = expiresIn > 60000 ? expiresIn - 60000 : 0;
          const timer = setTimeout(() => {
            checkAndRefreshToken();
          }, refreshTime);
          return () => clearTimeout(timer);
        }
      } catch (error) {
        console.error("Invalid token:", error);
      }
    }
  }, [accessToken]);

  // New: Listen for cookie changes via polling (simple approach)
  useEffect(() => {
    const interval = setInterval(() => {
      const newAccessToken = Cookies.get("access_token");
      if (newAccessToken !== accessToken) {
        setAccessToken(newAccessToken);
        checkAndRefreshToken();
      }
    }, 1000); // Check every second
    return () => clearInterval(interval);
  }, [accessToken]);

  return (
    <AuthContext.Provider value={{ isLoggedIn, subscriptionStatus, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
