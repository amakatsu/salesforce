import { createRequire } from 'node:module'
import path from 'node:path'
import process from 'node:process'
import { Client } from '@modelcontextprotocol/sdk/client'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
import { CallToolResultSchema, type CallToolResult } from '@modelcontextprotocol/sdk/types.js'

const require = createRequire(import.meta.url)
const PLAYWRIGHT_MCP_ENTRY = path.resolve(require.resolve('playwright-mcp/package.json'), '..', 'dist', 'server.js')

export interface RedmineSearchInput {
  baseUrl: string
  keyword: string
  max: number
  timeoutSeconds: number
  userDataDir?: string
}

export interface RedmineSearchHit {
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

export const runRedmineSearch = async (input: RedmineSearchInput): Promise<RedmineSearchHit[]> => {
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
    const message = error instanceof Error ? error.message : 'Redmine search failed'
    throw new Error(`Redmine検索に失敗しました: ${message}${stderrMessage}`)
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

const extractHits = (result: CallToolResult, baseUrl: string): RedmineSearchHit[] => {
  const payloadText = getTextContent(result)
  if (!payloadText) {
    return []
  }

  try {
    const payload = JSON.parse(payloadText)
    if (payload.error) {
      throw new Error(payload.message ?? 'execute-codeがエラーを返しました')
    }
    const rows = Array.isArray(payload.results) ? (payload.results as RedmineSearchHit[]) : []
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
  const url = new URL(baseUrl)
  const pathname = url.pathname.endsWith('/') ? url.pathname : `${url.pathname}/`
  url.pathname = `${pathname}search`
  url.search = ''
  url.searchParams.set('utf8', '\u2713')
  url.searchParams.set('q', keyword)
  url.searchParams.set('all_words', '1')
  return url.toString()
}

const buildExecuteScript = (searchUrl: string, maxItems: number, timeoutMs: number) => `async function run(page) {
  const targetUrl = ${JSON.stringify(searchUrl)};
  const timeoutMs = ${timeoutMs};
  const maxItems = ${maxItems};
  try {
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
    await page.waitForTimeout(500);
    await page.waitForSelector('#search-results .result', { timeout: timeoutMs }).catch(() => null);
    const results = await page.evaluate(({ maxItems, targetUrl }) => {
      const nodes = Array.from(document.querySelectorAll('#search-results .result'));
      return nodes.slice(0, maxItems).map((node) => {
        const anchor = node.querySelector('a');
        const description = node.querySelector('.description');
        const href = anchor?.getAttribute('href') ?? '';
        const absoluteUrl = href ? new URL(href, targetUrl).href : targetUrl;
        return {
          title: (anchor?.textContent ?? '').trim(),
          url: absoluteUrl,
          snippet: (description?.textContent ?? '').replace(/\\s+/g, ' ').trim(),
        };
      }).filter((item) => item.url);
    }, { maxItems, targetUrl });
    return { results, searchUrl: targetUrl };
  } catch (error) {
    return { error: true, message: error?.message ?? 'Search failed', results: [], searchUrl: targetUrl };
  }
}`
