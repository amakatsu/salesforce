import { z } from 'zod'

export const limitsSchema = z.object({
  localMaxResults: z.number().int().min(1).max(2000).default(200),
  redmineMaxResults: z.number().int().min(1).max(200).default(50),
  timeoutSeconds: z.number().int().min(5).max(300).default(30),
  scrollSteps: z.number().int().min(1).max(50).default(5),
})

export const settingsSchema = z.object({
  keyword: z.string().trim().default(''),
  ai: z
    .object({
      apiKey: z.string().trim().default(''),
      modelId: z.string().trim().default('openai/gpt-4o-mini'),
    })
    .default({}),
  local: z
    .object({
      root: z.array(z.string().min(1, 'Path is required')).default([]),
    })
    .default({}),
  redmine: z
    .object({
      urls: z.array(z.string().url('Redmine URL is invalid')).default([]),
    })
    .default({}),
  sharepoint: z
    .object({
      urls: z.array(z.string().url('SharePoint URL is invalid')).default([]),
    })
    .default({}),
  teams: z
    .object({
      urls: z.array(z.string().url('Teams URL is invalid')).default([]),
    })
    .default({}),
  internalDocs: z
    .object({
      baseUrl: z.string().url('Internal docs URL is invalid').or(z.literal('')).default(''),
    })
    .default({}),
  browser: z
    .object({
      userDataDir: z.string().trim().default(''),
    })
    .default({}),
  excludeGlobs: z.array(z.string().min(1)).default(['.git', 'node_modules', '.venv', 'target', 'dist']),
  limits: limitsSchema.default({}),
})

export type AppSettings = z.infer<typeof settingsSchema>

export const defaultSettings: AppSettings = settingsSchema.parse({})
