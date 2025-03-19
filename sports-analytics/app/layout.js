"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Cookies from "js-cookie";
import { jwtDecode } from "jwt-decode";
import NavBar from "../components/NavBar";
import "../styles/globals.css";

export default function Layout({ children }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [accessToken, setAccessToken] = useState(Cookies.get("access_token")); // New state

  const checkAndRefreshToken = async () => {
    const currentAccessToken = Cookies.get("access_token");
    const refreshToken = Cookies.get("refresh_token");
    let isUserLoggedIn = !!currentAccessToken && !!refreshToken;
    let currentSubscriptionStatus = localStorage.getItem("subscription_status");

    if (currentAccessToken) {
      try {
        const decodedToken = jwtDecode(currentAccessToken);
        const currentTime = Date.now() / 1000;

        if (decodedToken.exp < currentTime) {
          if (refreshToken) {
            const response = await fetch(
              `${process.env.NEXT_PUBLIC_API_BASE_URL}/token/refresh-token`,
              {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({ refreshToken }),
              }
            );

            if (response.ok) {
              const data = await response.json();
              const newAccessToken = data.accessToken;
              Cookies.set("access_token", newAccessToken, { path: "/" });
              setAccessToken(newAccessToken); // Update state to trigger refresh timer
              const newDecodedToken = jwtDecode(newAccessToken);
              currentSubscriptionStatus =
                newDecodedToken.subscription_status ||
                currentSubscriptionStatus;
              localStorage.setItem(
                "subscription_status",
                currentSubscriptionStatus
              );
              isUserLoggedIn = true;
            } else {
              isUserLoggedIn = false;
            }
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

    setIsLoggedIn(isUserLoggedIn);
    setSubscriptionStatus(currentSubscriptionStatus);
    setIsLoading(false);
  };

  // Check token on navigation
  useEffect(() => {
    checkAndRefreshToken();
  }, [pathname, router]);

  // Proactive token refresh before expiration
  useEffect(() => {
    if (accessToken) {
      try {
        const decodedToken = jwtDecode(accessToken);
        const currentTime = Date.now() / 1000;
        if (decodedToken.exp > currentTime) {
          const expiresIn = (decodedToken.exp - currentTime) * 1000; // Time until expiration in ms
          const refreshTime = expiresIn > 60000 ? expiresIn - 60000 : 0; // Refresh 60s before, or immediately if < 60s
          const timer = setTimeout(() => {
            checkAndRefreshToken();
          }, refreshTime);
          return () => clearTimeout(timer); // Cleanup to prevent multiple timers
        }
      } catch (error) {
        console.error("Invalid token:", error);
      }
    }
  }, [accessToken]);

  // Redirection logic
  useEffect(() => {
    if (!isLoading) {
      const publicPaths = [
        "/login",
        "/verify-email",
        "/register",
        "/password-reset",
        "/password-reset-confirm",
        "/termsandconditions",
      ];

      const isPublicPath =
        pathname === "/" ||
        publicPaths.some((path) => pathname.startsWith(path));

      if (isPublicPath) {
        // Allow access to public paths
      } else if (!isLoggedIn) {
        router.replace("/login");
      } else if (
        subscriptionStatus === "inactive" &&
        pathname !== "/checkout"
      ) {
        router.replace("/checkout");
      }
    }
  }, [isLoading, isLoggedIn, subscriptionStatus, pathname, router]);

  return (
    <html lang="en">
      <body>
        {isLoading ? (
          <div>Loading...</div>
        ) : (
          <>
            <NavBar />
            {children}
          </>
        )}
      </body>
    </html>
  );
}
