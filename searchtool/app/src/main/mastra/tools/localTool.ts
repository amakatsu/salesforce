import { createTool } from '@mastra/core/tools'
import { z } from 'zod'
import { invokeMcp } from './mcpClient'

const localSearchOutputSchema = z.object({
  results: z.array(
    z.object({
      path: z.string(),
      line: z.number(),
      snippet: z.string(),
    }),
  ),
})

const localSearchInputSchema = z.object({
  root: z.array(z.string().min(1)).nonempty(),
  query: z.string().min(1),
  max: z.number().int().min(1).max(2000).default(200),
  excludeGlobs: z.array(z.string().min(1)).optional(),
})

export const localSearchTool = createTool({
  id: 'mcp_local_search',
  description: 'MCP local.searchでローカルディレクトリを全文検索します。',
  inputSchema: localSearchInputSchema,
  outputSchema: localSearchOutputSchema,
  execute: async ({ context }) => {
    const payload = localSearchInputSchema.parse(context)
    const result = (await invokeMcp('local.search', payload)) as z.infer<typeof localSearchOutputSchema>
    return result
  },
})
