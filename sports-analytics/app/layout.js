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
    const accessToken = Cookies.get("access_token");
    const refreshToken = Cookies.get("refresh_token");
    const isUserLoggedIn = !!accessToken && !!refreshToken;
    setIsLoggedIn(isUserLoggedIn);

    const subscriptionStatus = localStorage.getItem("subscription_status");

    const publicPaths = [
      "/login",
      "/verify-email",
      "/register",
      "/password-reset",
      "/password-reset-confirm",
    ];

    const isPublicPath =
      pathname === "/" || publicPaths.some((path) => pathname.startsWith(path));

    if (isPublicPath) {
      // Allow access to public paths
    } else if (!isUserLoggedIn) {
      // Redirect to /login if not logged in
      router.replace("/login");
    } else if (subscriptionStatus === "inactive" && pathname !== "/checkout") {
      // Redirect to /checkout if logged in but subscription is inactive
      router.replace("/checkout");
    } else {
      // Allow access to protected paths or /checkout if logged in
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
