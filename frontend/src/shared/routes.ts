import { z } from "zod";
import {
  careerRecommendationResponseSchema,
  historyResponseSchema,
  errorResponseSchema,
  authResponseSchema,
  chatResponseSchema,
} from "./schema";

// ============= API Base Configuration =============

const API_BASE = "/api";

// Get auth token from localStorage
function getAuthToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("auth_token");
  }
  return null;
}

// Build headers with optional auth
function buildHeaders(includeAuth: boolean = false): HeadersInit {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  
  if (includeAuth) {
    const token = getAuthToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  
  return headers;
}

// ============= URL Builder =============

export function buildUrl(path: string, params?: Record<string, string>): string {
  const url = new URL(path, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.set(key, value);
    });
  }
  return url.pathname + url.search;
}

// ============= API Routes =============

export const api = {
  // Career endpoints
  career: {
    recommend: {
      path: `${API_BASE}/recommend`,
      method: "POST" as const,
      responses: {
        200: careerRecommendationResponseSchema,
        400: errorResponseSchema,
        500: errorResponseSchema,
      },
    },
    history: {
      path: `${API_BASE}/history`,
      method: "GET" as const,
      responses: {
        200: historyResponseSchema,
        401: errorResponseSchema,
      },
    },
    historyItem: {
      path: (id: number) => `${API_BASE}/history/${id}`,
      method: "GET" as const,
      responses: {
        200: careerRecommendationResponseSchema,
        404: errorResponseSchema,
      },
    },
  },
  
  // Auth endpoints
  auth: {
    login: {
      path: `${API_BASE}/auth/login`,
      method: "POST" as const,
      responses: {
        200: authResponseSchema,
        401: errorResponseSchema,
      },
    },
    register: {
      path: `${API_BASE}/auth/register`,
      method: "POST" as const,
      responses: {
        200: authResponseSchema,
        400: errorResponseSchema,
      },
    },
    me: {
      path: `${API_BASE}/auth/me`,
      method: "GET" as const,
      responses: {
        200: z.object({
          id: z.number(),
          name: z.string(),
          email: z.string(),
        }),
        401: errorResponseSchema,
      },
    },
  },
  
  // Chat endpoints
  chat: {
    message: {
      path: `${API_BASE}/chat`,
      method: "POST" as const,
      responses: {
        200: chatResponseSchema,
        500: errorResponseSchema,
      },
    },
  },
};

// ============= API Client Helper =============

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  requireAuth: boolean = false
): Promise<T> {
  const headers = buildHeaders(requireAuth);
  
  const response = await fetch(path, {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Request failed" }));
    throw new Error(error.message || error.detail || "Request failed");
  }
  
  return response.json();
}

// ============= Typed API Functions =============

export const apiClient = {
  // Career
  async recommend(data: {
    educationLevel: string;
    interests: string[];
    hobbies: string[];
    skills: string[];
    personalityTraits: string[];
    extraInfo: string;
  }) {
    return apiRequest<z.infer<typeof careerRecommendationResponseSchema>>(
      api.career.recommend.path,
      {
        method: "POST",
        body: JSON.stringify(data),
      },
      false // Guest mode - no auth required
    );
  },
  
  async getHistory() {
    return apiRequest<z.infer<typeof historyResponseSchema>>(
      api.career.history.path,
      { method: "GET" },
      true // Auth required for history
    );
  },
  
  async getHistoryItem(id: number) {
    return apiRequest<z.infer<typeof careerRecommendationResponseSchema>>(
      api.career.historyItem.path(id),
      { method: "GET" },
      true
    );
  },
  
  // Auth
  async login(email: string, password: string) {
    return apiRequest<z.infer<typeof authResponseSchema>>(
      api.auth.login.path,
      {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }
    );
  },
  
  async register(name: string, email: string, password: string) {
    return apiRequest<z.infer<typeof authResponseSchema>>(
      api.auth.register.path,
      {
        method: "POST",
        body: JSON.stringify({ name, email, password }),
      }
    );
  },
  
  async getCurrentUser() {
    return apiRequest<{ id: number; name: string; email: string }>(
      api.auth.me.path,
      { method: "GET" },
      true
    );
  },
  
  // Chat
  async sendMessage(message: string, context?: string) {
    return apiRequest<z.infer<typeof chatResponseSchema>>(
      api.chat.message.path,
      {
        method: "POST",
        body: JSON.stringify({ message, context }),
      },
      false // Chat works in guest mode
    );
  },
};
