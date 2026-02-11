import { createRequire } from 'node:module'
import path from 'node:path'
import process from 'node:process'
import { Client } from '@modelcontextprotocol/sdk/client'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
import { CallToolResultSchema, type CallToolResult } from '@modelcontextprotocol/sdk/types.js'

const require = createRequire(import.meta.url)
const PLAYWRIGHT_MCP_ENTRY = path.resolve(require.resolve('playwright-mcp/package.json'), '..', 'dist', 'server.js')

export interface TeamsSearchInput {
  baseUrl: string
  keyword: string
  max: number
  timeoutSeconds: number
  userDataDir?: string
}

export interface TeamsSearchHit {
  title: string
  url: string
  snippet: string
}

const createTransport = (userDataDir?: string) =>
  new StdioClientTransport({
    command: process.execPath,
    args: [PLAYWRIGHT_MCP_ENTRY],
    env: {
      ...process.env,
      PLAYWRIGHT_MCP_PROFILE_DIR: userDataDir ?? '',
    },
    stderr: 'pipe',
  })

export const runTeamsSearch = async (input: TeamsSearchInput): Promise<TeamsSearchHit[]> => {
  if (!input.baseUrl) {
    return []
  }
  const maxItems = Math.max(1, Math.min(input.max, 100))
  const timeoutMs = Math.max(5, input.timeoutSeconds) * 1000
  const transport = createTransport(input.userDataDir)
  const stderrChunks: string[] = []
  const stderrStream = transport.stderr as NodeJS.ReadableStream | null
  if (stderrStream) {
    stderrStream.setEncoding('utf-8')
    stderrStream.on('data', (chunk: string) => stderrChunks.push(chunk))
  }

  const client = new Client({
    name: 'SearchTool',
    version: '0.0.0',
  })

  try {
    await client.connect(transport)
    const searchUrl = buildSearchUrl(input.baseUrl, input.keyword)

    await callTool(client, 'init-browser', { url: searchUrl }, timeoutMs)
    const execResult = await callTool(
      client,
      'execute-code',
      {
        code: buildExecuteScript(searchUrl, maxItems, timeoutMs),
      },
      timeoutMs,
    )

    return extractHits(execResult, input.baseUrl).slice(0, maxItems)
  } catch (error) {
    const stderrMessage = stderrChunks.length ? `\n[playwright-mcp] ${stderrChunks.join('')}` : ''
    const message = error instanceof Error ? error.message : 'Teams search failed'
    throw new Error(`Teams検索に失敗しました: ${message}${stderrMessage}`)
  } finally {
    await client.close().catch(() => undefined)
  }
}

const callTool = async (client: Client, name: string, args: Record<string, unknown>, timeout: number) => {
  const result = await client.request(
    {
      method: 'tools/call',
      params: {
        name,
        arguments: args,
      },
    },
    CallToolResultSchema,
    { timeout },
  )

  if (!result) {
    throw new Error(`${name} ツールが結果を返しませんでした`)
  }

  if (result.isError) {
    throw new Error(getTextContent(result) ?? `${name} ツールでエラーが発生しました`)
  }

  return result
}

const extractHits = (result: CallToolResult, baseUrl: string): TeamsSearchHit[] => {
  const payloadText = getTextContent(result)
  if (!payloadText) {
    return []
  }

  try {
    const payload = JSON.parse(payloadText)
    if (payload.error) {
      throw new Error(payload.message ?? 'execute-codeがエラーを返しました')
    }
    const rows = Array.isArray(payload.results) ? (payload.results as TeamsSearchHit[]) : []
    return rows
      .map((item) => ({
        title: (item?.title ?? '').trim(),
        url: toAbsoluteUrl(item?.url ?? '', baseUrl),
        snippet: (item?.snippet ?? '').trim(),
      }))
      .filter((item) => item.url)
  } catch (error) {
    throw new Error(`execute-codeの結果解析に失敗しました: ${(error as Error).message}`)
  }
}

const getTextContent = (result: CallToolResult) =>
  result.content.find((entry): entry is { type: 'text'; text: string } => entry.type === 'text')?.text ?? null

const toAbsoluteUrl = (rawUrl: string, baseUrl: string) => {
  if (!rawUrl) return ''
  try {
    return new URL(rawUrl, baseUrl).toString()
  } catch {
    return rawUrl
  }
}

const buildSearchUrl = (baseUrl: string, keyword: string) => {
  // Teams Web URLを構築
  const url = new URL(baseUrl)
  if (url.hostname.includes('teams.microsoft.com')) {
    url.pathname = '/_'
    url.hash = `/search/messages/${encodeURIComponent(keyword)}`
  } else {
    // カスタムURLの場合
    url.search = ''
    url.searchParams.set('search', keyword)
  }
  return url.toString()
}

const buildExecuteScript = (searchUrl: string, maxItems: number, timeoutMs: number) => `async function run(page) {
  const targetUrl = ${JSON.stringify(searchUrl)};
  const timeoutMs = ${timeoutMs};
  const maxItems = ${maxItems};
  try {
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
    await page.waitForTimeout(3000);

    // Teamsの検索結果を待つ
    await page.waitForSelector('[data-tid="search-result-item"], .search-result, [class*="searchResult"]', { timeout: timeoutMs }).catch(() => null);

    const results = await page.evaluate(({ maxItems, targetUrl }) => {
      // Teamsの検索結果パターンに対応
      const selectors = [
        '[data-tid="search-result-item"]',
        '.search-result-item',
        '[class*="searchResult"]',
        '[role="listitem"]',
      ];

      let nodes = [];
      for (const selector of selectors) {
        nodes = Array.from(document.querySelectorAll(selector));
        if (nodes.length > 0) break;
      }

      return nodes.slice(0, maxItems).map((node, index) => {
        const titleElement = node.querySelector('[class*="subject"], [class*="title"], h3, h4');
        const messageElement = node.querySelector('[class*="message"], [class*="content"], p');
        const linkElement = node.querySelector('a[href]');

        const title = titleElement?.textContent || \`Teams Result \${index + 1}\`;
        const snippet = messageElement?.textContent || '';
        const href = linkElement?.getAttribute('href') || targetUrl;
        const absoluteUrl = href.startsWith('http') ? href : new URL(href, targetUrl).href;

        return {
          title: title.trim(),
          url: absoluteUrl,
          snippet: snippet.replace(/\\s+/g, ' ').trim().substring(0, 300),
        };
      }).filter((item) => item.title && item.url);
    }, { maxItems, targetUrl });

    return { results, searchUrl: targetUrl };
  } catch (error) {
    return { error: true, message: error?.message ?? 'Search failed', results: [], searchUrl: targetUrl };
  }
}`
