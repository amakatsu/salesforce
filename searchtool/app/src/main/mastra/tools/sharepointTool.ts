import { createTool } from '@mastra/core'
import { z } from 'zod'
import { invokeMcp } from './mcpClient'

export const sharepointSearchTool = createTool({
  id: 'sharepoint.search',
  description:
    'SharePointで指定されたキーワードを検索し、関連するドキュメントやページを取得します。社内のSharePointサイトに保存された情報を検索する際に使用します。',
  inputSchema: z.object({
    baseUrl: z.string().url().describe('SharePointサイトのベースURL'),
    keyword: z.string().min(1).describe('検索キーワード'),
    max: z.number().int().min(1).max(100).default(50).describe('最大取得件数'),
    timeoutSeconds: z.number().int().min(5).max(300).default(30).describe('タイムアウト(秒)'),
    userDataDir: z.string().optional().describe('ブラウザプロファイルディレクトリ'),
  }),
  outputSchema: z.object({
    results: z.array(
      z.object({
        title: z.string(),
        url: z.string(),
        snippet: z.string(),
      }),
    ),
  }),
  execute: async ({ context }): Promise<{
    results: Array<{ title: string; url: string; snippet: string }>
  }> => {
    const { baseUrl, keyword, max, timeoutSeconds, userDataDir } = context
    const result = await invokeMcp('sharepoint.search' as const, {
      baseUrl,
      keyword,
      max,
      timeoutSeconds,
      userDataDir,
    })
    return result as { results: Array<{ title: string; url: string; snippet: string }> }
  },
})
