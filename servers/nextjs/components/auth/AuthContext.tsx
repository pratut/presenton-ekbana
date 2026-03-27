"use client";

import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import {
  FrontendAuthSession,
  fetchBackendSession,
  loginWithBackend,
  logoutFromBackend,
} from "@/utils/authSession";

interface AuthContextValue {
  session: FrontendAuthSession | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [session, setSession] = useState<FrontendAuthSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const bootstrap = async () => {
      const nextSession = await fetchBackendSession();
      setSession(nextSession);
      setIsLoading(false);
    };
    bootstrap();
  }, []);

  const login = async (email: string, password: string) => {
    const nextSession = await loginWithBackend(email, password);
    setSession(nextSession);
  };

  const logout = async () => {
    await logoutFromBackend();
    setSession(null);
  };

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      isLoading,
      isAuthenticated: !!session,
      login,
      logout,
    }),
    [session, isLoading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
};
