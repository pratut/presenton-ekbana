export interface FrontendAuthSession {
  sessionId: string;
  email: string;
  displayName: string;
  createdAt: number;
}

const AUTH_SESSION_KEY = "ekbana:auth:session";

const safeJsonParse = <T>(value: string | null): T | null => {
  if (!value) return null;
  try {
    return JSON.parse(value) as T;
  } catch {
    return null;
  }
};

const EMAIL_REGEX =
  /^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$/i;

export const getStoredAuthSession = (): FrontendAuthSession | null => {
  if (typeof window === "undefined") return null;
  return safeJsonParse<FrontendAuthSession>(window.localStorage.getItem(AUTH_SESSION_KEY));
};

export const setStoredAuthSession = (session: FrontendAuthSession) => {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(session));
};

export const clearStoredAuthSession = () => {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(AUTH_SESSION_KEY);
};

const parseSessionResponse = (payload: unknown): FrontendAuthSession => {
  const data = payload as {
    sessionId?: string;
    email?: string;
    displayName?: string;
  };
  if (!data?.sessionId || !data?.email || !data?.displayName) {
    throw new Error("Invalid session response from server.");
  }
  const session: FrontendAuthSession = {
    sessionId: data.sessionId,
    email: data.email,
    displayName: data.displayName,
    createdAt: Date.now(),
  };
  setStoredAuthSession(session);
  return session;
};

export const loginWithBackend = async (email: string, password: string) => {
  const normalizedEmail = email.trim().toLowerCase();
  const trimmedPassword = password.trim();

  if (!normalizedEmail || !EMAIL_REGEX.test(normalizedEmail)) {
    throw new Error("Please enter a valid email address.");
  }
  if (trimmedPassword.length < 6) {
    throw new Error("Password must be at least 6 characters.");
  }

  const response = await fetch("/api/v1/auth/login", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: normalizedEmail,
      password: trimmedPassword,
    }),
  });

  if (!response.ok) {
    const errorPayload = safeJsonParse<{ detail?: string }>(await response.text()) || {};
    throw new Error(errorPayload.detail || "Invalid email or password.");
  }

  const payload = await response.json();
  return parseSessionResponse(payload);
};

export const fetchBackendSession = async (): Promise<FrontendAuthSession | null> => {
  const response = await fetch("/api/v1/auth/me", {
    method: "GET",
    credentials: "include",
  });
  if (!response.ok) {
    clearStoredAuthSession();
    return null;
  }
  const payload = await response.json();
  return parseSessionResponse(payload);
};

export const logoutFromBackend = async () => {
  try {
    await fetch("/api/v1/auth/logout", {
      method: "POST",
      credentials: "include",
    });
  } finally {
    clearStoredAuthSession();
  }
};
