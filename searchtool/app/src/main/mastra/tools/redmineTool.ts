import { createTool } from '@mastra/core/tools'
import { z } from 'zod'
import { invokeMcp } from './mcpClient'

const redmineSearchOutputSchema = z.object({
  results: z.array(
    z.object({
      title: z.string(),
      url: z.string(),
      snippet: z.string(),
    }),
  ),
})

const redmineSearchInputSchema = z.object({
  baseUrl: z.string().url(),
  keyword: z.string().min(1),
  max: z.number().int().min(1).max(200).default(50),
  timeoutSeconds: z.number().int().min(5).max(120).default(30),
  userDataDir: z.string().optional(),
})

export const redmineSearchTool = createTool({
  id: 'mcp_redmine_search',
  description: 'playwright-mcp経由でRedmineの検索UIをスクレイピングし、結果を要約します。',
  inputSchema: redmineSearchInputSchema,
  outputSchema: redmineSearchOutputSchema,
  execute: async ({ context }) => {
    const payload = redmineSearchInputSchema.parse(context)
    const result = (await invokeMcp('redmine.search', payload)) as z.infer<typeof redmineSearchOutputSchema>
    return result
  },
})
