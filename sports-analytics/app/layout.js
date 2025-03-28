"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Cookies from "js-cookie";
import { jwtDecode } from "jwt-decode";
import NavBar from "../components/NavBar";
import "../styles/globals.css";
import { AuthProvider, useAuth } from "./contexts/AuthContext"; // Updated path

// New child component to use useAuth within AuthProvider
function LayoutContent({ children }) {
  const router = useRouter();
  const pathname = usePathname();
  const {
    isLoggedIn: contextIsLoggedIn,
    subscriptionStatus: contextSubscriptionStatus,
    isLoading: contextIsLoading,
  } = useAuth();

  useEffect(() => {
    if (!contextIsLoading) {
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
      } else if (!contextIsLoggedIn) {
        router.replace("/login");
      } else if (
        contextSubscriptionStatus === "inactive" &&
        pathname !== "/checkout"
      ) {
        router.replace("/checkout");
      }
    }
  }, [
    contextIsLoading,
    contextIsLoggedIn,
    contextSubscriptionStatus,
    pathname,
    router,
  ]);

  return contextIsLoading ? (
    <div>Loading...</div>
  ) : (
    <>
      <NavBar />
      {children}
    </>
  );
}

export default function Layout({ children }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [accessToken, setAccessToken] = useState(Cookies.get("access_token"));

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
              setAccessToken(newAccessToken);
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

  useEffect(() => {
    checkAndRefreshToken();
  }, [pathname, router]);

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

  useEffect(() => {
    console.log("isLoggedIn updated:", isLoggedIn);
  }, [isLoggedIn]);

  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <LayoutContent>{children}</LayoutContent>
        </AuthProvider>
      </body>
    </html>
  );
}
