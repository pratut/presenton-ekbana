import { LLMConfig } from "@/types/llm_config";

const getScopedConfigKey = (sessionId: string) => `ekbana:user:${sessionId}:llmConfig`;

const safeParseConfig = (value: string | null): LLMConfig | null => {
  if (!value) return null;
  try {
    return JSON.parse(value) as LLMConfig;
  } catch {
    return null;
  }
};

export const getUserScopedLLMConfig = (sessionId?: string): LLMConfig | null => {
  if (typeof window === "undefined" || !sessionId) return null;
  return safeParseConfig(window.localStorage.getItem(getScopedConfigKey(sessionId)));
};

export const setUserScopedLLMConfig = (sessionId: string, llmConfig: LLMConfig) => {
  if (typeof window === "undefined" || !sessionId) return;
  window.localStorage.setItem(getScopedConfigKey(sessionId), JSON.stringify(llmConfig));
};
