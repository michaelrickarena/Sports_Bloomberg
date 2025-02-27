"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Cookies from "js-cookie";
import NavBar from "../components/NavBar";
import "../styles/globals.css";

export default function Layout({ children }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    console.log("All Cookies:", document.cookie);

    const accessToken = Cookies.get("access_token");
    const refreshToken = Cookies.get("refresh_token");
    console.log("Access Token:", accessToken);
    console.log("Refresh Token:", refreshToken);

    const isUserLoggedIn = !!accessToken && !!refreshToken;
    setIsLoggedIn(isUserLoggedIn);

    const subscriptionStatus = localStorage.getItem("subscription_status");
    console.log("Subscription Status:", subscriptionStatus);

    const publicPaths = [
      "/login",
      "/verify-email",
      "/register",
      "/",
      "/checkout",
      "/password-reset",
      "/password-reset-confirm", // Base path for dynamic route
    ];

    // Check if the current pathname starts with any public path
    const isPublicPath = publicPaths.some((path) => pathname.startsWith(path));

    // Restrict access if the user is inactive or not logged in
    if (
      (!isUserLoggedIn || subscriptionStatus === "inactive") &&
      !isPublicPath
    ) {
      console.log("Access restricted: Redirecting to /login...");
      router.replace("/login");
    } else {
      console.log("User is logged in or on a public path. Access granted.");
    }
  }, [pathname, router]);

  return (
    <html lang="en">
      <head />
      <body>
        <NavBar />
        {children}
      </body>
    </html>
  );
}
