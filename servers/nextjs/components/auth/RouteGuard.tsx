"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "./AuthContext";

const PUBLIC_PATHS = new Set(["/login"]);

export const RouteGuard = ({ children }: { children: React.ReactNode }) => {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (isLoading) return;
    const isPublicPath = PUBLIC_PATHS.has(pathname);

    if (!isAuthenticated && !isPublicPath) {
      router.replace("/login");
      return;
    }
    if (isAuthenticated && pathname === "/login") {
      router.replace("/");
    }
  }, [isAuthenticated, isLoading, pathname, router]);

  if (isLoading) return null;
  if (!isAuthenticated && !PUBLIC_PATHS.has(pathname)) return null;
  if (isAuthenticated && pathname === "/login") return null;

  return <>{children}</>;
};
