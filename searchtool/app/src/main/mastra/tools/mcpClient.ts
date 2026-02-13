import { z } from 'zod'
import { runLocalSearch } from '../../mcp-servers/local-fs.server'
import { runRedmineSearch } from '../../mcp-servers/redmine-ui.server'
import { runSharePointSearch } from '../../mcp-servers/sharepoint-search.server'

const localSearchInputSchema = z.object({
  root: z.array(z.string().min(1)).nonempty(),
  query: z.string().min(1),
  max: z.number().int().min(1).max(2000).default(200),
  excludeGlobs: z.array(z.string().min(1)).optional(),
})

const webSearchInputSchema = z.object({
  baseUrl: z.string().url(),
  keyword: z.string().min(1),
  max: z.number().int().min(1).max(200).default(50),
  timeoutSeconds: z.number().int().min(5).max(120).default(30),
  userDataDir: z.string().optional(),
})

export type McpToolName =
  | 'local.search'
  | 'redmine.search'
  | 'sharepoint.search'

export const invokeMcp = async (toolName: McpToolName, payload: unknown): Promise<unknown> => {
  switch (toolName) {
    case 'local.search': {
      const parsed = localSearchInputSchema.parse(payload)
      const results = await runLocalSearch(parsed)
      return { results }
    }
    case 'redmine.search': {
      const parsed = webSearchInputSchema.parse(payload)
      const results = await runRedmineSearch(parsed)
      return { results }
    }
    case 'sharepoint.search': {
      const parsed = webSearchInputSchema.parse(payload)
      const results = await runSharePointSearch(parsed)
      return { results }
    }
    default:
      throw new Error(`Unsupported MCP tool: ${toolName}`)
  }
}
