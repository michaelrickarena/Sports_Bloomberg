"use client";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Script from "next/script";
import Cookies from "js-cookie";
import { jwtDecode } from "jwt-decode";
import NavBar from "../components/NavBar";
import { AuthProvider, useAuth } from "./contexts/AuthContext";

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
        "/privacy",
        "/calculators/arbitrage",
        "/calculators/expected-value",
        "/calculators/hedge",
        "/calculators/implied-odds",
        "/calculators/kelly-criterion",
        "/calculators/no-vig",
        "/calculators/odds-conversion",
        "/calculators/parlay",
        "/blogs/arbitrage",
        "/blogs/expected-value",
        "/blogs/historical-data",
        "/blogs/implied-odds",
        "/blogs/kelly-criterion",
        "/blogs/no-vig",
        "/blogs/z-score",
        "/blogs",
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
      <Script
        id="org-ld-json"
        type="application/ld+json"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Organization",
            name: "The Smart Lines",
            url: "https://www.thesmartlines.com",
            logo: "https://www.thesmartlines.com/assets/images/logo-small.png",
          }),
        }}
      />
      <link rel="icon" href="/favicon.ico" />
      <NavBar />
      {children}
    </>
  );
}

export default function ClientLayout({ children }) {
  return (
    <AuthProvider>
      <LayoutContent>{children}</LayoutContent>
    </AuthProvider>
  );
}
