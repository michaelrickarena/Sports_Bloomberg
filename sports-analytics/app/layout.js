"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Cookies from "js-cookie";
import NavBar from "../components/NavBar";
import "../styles/globals.css";

export default function Layout({ children }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState(false); // Track login status

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    // Set login status based on presence of token
    setIsLoggedIn(!!token);

    // Define public paths that should be accessible without authentication
    const publicPaths = ["/login", "/register", "/", "/checkout"];

    // If not logged in and accessing a protected route, redirect to login
    if (!token && !publicPaths.includes(pathname)) {
      router.replace("/login");
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
