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
    // Log all available cookies
    console.log("All Cookies:", document.cookie);

    // Check for both access_token and refresh_token in cookies
    const accessToken = Cookies.get("access_token");
    const refreshToken = Cookies.get("refresh_token");

    console.log("Access Token:", accessToken);
    console.log("Refresh Token:", refreshToken);

    // Set login state based on presence of both tokens
    const isUserLoggedIn = !!accessToken && !!refreshToken;
    setIsLoggedIn(isUserLoggedIn);

    console.log("User logged in:", isUserLoggedIn);

    const publicPaths = [
      "/login",
      "/verify-email",
      "/register",
      "/",
      "/checkout",
    ];

    // If no token and user is not on a public path, redirect to login
    if (!isUserLoggedIn && !publicPaths.includes(pathname)) {
      console.log("No valid token, redirecting to /login...");
      router.replace("/login");
    } else {
      console.log("User is logged in or on a public path.");
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
