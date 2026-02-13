import { createTool } from '@mastra/core/tools'
import { z } from 'zod'

// ---------------------------------------------------------------------------
// Schema（tool_interfaces.md §3b 準拠）
// ---------------------------------------------------------------------------

const searchHitSchema = z.object({
  title: z.string(),
  url: z.string(),
  snippet: z.string(),
  lastModified: z.string().optional(),
})

type SearchHit = z.infer<typeof searchHitSchema>

const inputSchema = z.object({
  pageSnapshot: z.string().min(1)
    .describe('browser_snapshot で取得したアクセシビリティスナップショット'),
  sourceType: z.enum(['sharepoint', 'teams', 'redmine', 'generic']).default('sharepoint')
    .describe('スナップショットの出典。抽出ヒントとして使用'),
  maxResults: z.number().int().min(1).max(100).default(20)
    .describe('抽出する最大件数'),
})

const outputSchema = z.object({
  results: z.array(searchHitSchema),
  confidence: z.enum(['high', 'medium', 'low'])
    .describe('抽出の確信度'),
  itemsFound: z.number().int()
    .describe('スナップショット内で検出した候補要素数'),
  interpretation: z.string().optional()
    .describe('スナップショットの解釈説明（デバッグ用）'),
})

// ---------------------------------------------------------------------------
// スナップショットからリンク要素を抽出
// ---------------------------------------------------------------------------

interface RawLink {
  title: string
  url: string
  context: string
}

const NAV_KEYWORDS = [
  'home', 'ホーム', 'login', 'ログイン', 'sign in', 'サインイン',
  'navigation', 'menu', 'footer', 'header', 'skip', 'logo',
]

const isNavigationLink = (title: string): boolean => {
  const lower = title.toLowerCase()
  return title.length < 2 || NAV_KEYWORDS.some(kw => lower.includes(kw))
}

const extractLinks = (snapshot: string): RawLink[] => {
  const linkPattern = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g
  const links: RawLink[] = []
  const lines = snapshot.split('\n')

  for (let i = 0; i < lines.length; i++) {
    linkPattern.lastIndex = 0
    let match: RegExpExecArray | null

    while ((match = linkPattern.exec(lines[i])) !== null) {
      const title = match[1].trim()
      const url = match[2]

      if (isNavigationLink(title)) continue

      const contextLines = lines
        .slice(i + 1, Math.min(lines.length, i + 4))
        .map(l => l.trim())
        .filter(l => l.length > 0 && !/\[([^\]]+)\]\(https?:/.test(l))

      links.push({
        title,
        url,
        context: contextLines.join(' ').slice(0, 300),
      })
    }
  }

  return links
}

// ---------------------------------------------------------------------------
// confidence 判定
// ---------------------------------------------------------------------------

const judgeConfidence = (hits: SearchHit[]): 'high' | 'medium' | 'low' => {
  if (hits.length === 0) return 'low'

  const complete = hits.filter(
    h => h.title.length > 0 && h.url.startsWith('http') && h.snippet.length > 0,
  )

  if (complete.length >= 3 && complete.length === hits.length) return 'high'
  if (complete.length > 0) return 'medium'
  return 'low'
}

// ---------------------------------------------------------------------------
// ExtractTool
// ---------------------------------------------------------------------------

/**
 * アクセシビリティスナップショットから検索結果を構造化データに変換する。
 * ブラウザ操作は一切行わない（純粋関数）。
 *
 * 解釈の主体は Agent。このツールはスナップショット内のリンク要素を
 * 機械的に検出し、構造化された出力形式で返す。
 */
export const extractTool = createTool({
  id: 'extract',
  description:
    'アクセシビリティスナップショットから検索結果を構造化データに変換する。' +
    'ブラウザ操作は行わない（純粋関数）。',
  inputSchema,
  outputSchema,
  execute: async ({ context }) => {
    const rawLinks = extractLinks(context.pageSnapshot)

    const results: SearchHit[] = rawLinks
      .slice(0, context.maxResults)
      .map(link => ({
        title: link.title,
        url: link.url,
        snippet: link.context || link.title,
      }))

    const confidence = judgeConfidence(results)

    return {
      results,
      confidence,
      itemsFound: rawLinks.length,
      interpretation: `sourceType=${context.sourceType}, ${rawLinks.length}件の候補リンクを検出`,
    }
  },
})
