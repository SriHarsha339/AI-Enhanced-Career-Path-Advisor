import { z } from "zod";

// ============= Input Schemas =============

export const insertCareerQuerySchema = z.object({
  educationLevel: z.string().min(1, "Please select your education level"),
  interests: z.array(z.string()).min(1, "Add at least one interest"),
  hobbies: z.array(z.string()).default([]),
  skills: z.array(z.string()).default([]),
  personalityTraits: z.array(z.string()).default([]),
  extraInfo: z.string().default(""),
});

export type CareerQueryInput = z.infer<typeof insertCareerQuerySchema>;

// ============= Response Schemas =============

export const landscapeItemSchema = z.object({
  title: z.string(),
  salary: z.string(),
  demand: z.string(),
  description: z.string(),
});

export const featuredCareerSchema = z.object({
  title: z.string(),
  alignment: z.string(),
  passion: z.string(),
  outlook: z.string(),
});

export const roadmapItemSchema = z.object({
  phase: z.string(),
  title: z.string(),
  duration: z.string(),
  details: z.string(),
});

export const structuredDataSchema = z.object({
  landscape: z.array(landscapeItemSchema),
  featured: featuredCareerSchema,
  roadmap: z.array(roadmapItemSchema),
  steps: z.array(z.string()),
});

export const careerRecommendationResponseSchema = z.object({
  queryId: z.number(),
  recommendation: z.string(),
  structuredData: structuredDataSchema,
});

export type CareerRecommendationResponse = z.infer<typeof careerRecommendationResponseSchema>;

// ============= History Schemas =============

export const historyItemSchema = z.object({
  id: z.number(),
  queryId: z.number(),
  educationLevel: z.string(),
  interests: z.array(z.string()),
  hobbies: z.array(z.string()),
  skills: z.array(z.string()),
  personalityTraits: z.array(z.string()),
  extraInfo: z.string().nullable(),
  topCareer: z.string(),
  createdAt: z.string(),
});

export const historyResponseSchema = z.array(historyItemSchema);

export type HistoryItem = z.infer<typeof historyItemSchema>;
export type HistoryResponse = z.infer<typeof historyResponseSchema>;

// ============= Auth Schemas =============

export const loginSchema = z.object({
  email: z.string().email("Please enter a valid email"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

export const registerSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email"),
  password: z.string().min(6, "Password must be at least 6 characters"),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;

export const authResponseSchema = z.object({
  access_token: z.string(),
  token_type: z.string(),
  user: z.object({
    id: z.number(),
    name: z.string(),
    email: z.string(),
  }),
});

export type AuthResponse = z.infer<typeof authResponseSchema>;

// ============= Error Schemas =============

export const errorResponseSchema = z.object({
  message: z.string(),
  detail: z.string().optional(),
});

export type ErrorResponse = z.infer<typeof errorResponseSchema>;

// ============= Chat Schemas =============

export const chatMessageSchema = z.object({
  role: z.enum(["user", "assistant"]),
  content: z.string(),
});

export const chatRequestSchema = z.object({
  message: z.string().min(1),
  context: z.string().optional(),
});

export const chatResponseSchema = z.object({
  response: z.string(),
});

export type ChatMessage = z.infer<typeof chatMessageSchema>;
export type ChatRequest = z.infer<typeof chatRequestSchema>;
export type ChatResponse = z.infer<typeof chatResponseSchema>;
