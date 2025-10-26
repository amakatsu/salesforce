import { createRequire } from 'node:module'
import path from 'node:path'
import process from 'node:process'
import { Client } from '@modelcontextprotocol/sdk/client'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
import { CallToolResultSchema, type CallToolResult } from '@modelcontextprotocol/sdk/types.js'

const require = createRequire(import.meta.url)
const PLAYWRIGHT_MCP_ENTRY = path.resolve(require.resolve('playwright-mcp/package.json'), '..', 'dist', 'server.js')

export interface InternalDocsSearchInput {
  baseUrl: string
  keyword: string
  max: number
  timeoutSeconds: number
  userDataDir?: string
}

export interface InternalDocsSearchHit {
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

export const runInternalDocsSearch = async (input: InternalDocsSearchInput): Promise<InternalDocsSearchHit[]> => {
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
        code: buildExecuteScript(searchUrl, input.keyword, maxItems, timeoutMs),
      },
      timeoutMs,
    )

    return extractHits(execResult, input.baseUrl).slice(0, maxItems)
  } catch (error) {
    const stderrMessage = stderrChunks.length ? `\n[playwright-mcp] ${stderrChunks.join('')}` : ''
    const message = error instanceof Error ? error.message : 'Internal docs search failed'
    throw new Error(`社内ドキュメント検索に失敗しました: ${message}${stderrMessage}`)
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

const extractHits = (result: CallToolResult, baseUrl: string): InternalDocsSearchHit[] => {
  const payloadText = getTextContent(result)
  if (!payloadText) {
    return []
  }

  try {
    const payload = JSON.parse(payloadText)
    if (payload.error) {
      throw new Error(payload.message ?? 'execute-codeがエラーを返しました')
    }
    const rows = Array.isArray(payload.results) ? (payload.results as InternalDocsSearchHit[]) : []
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

const buildSearchUrl = (baseUrl: string, _keyword: string) => {
  // 自動検索欄検出を使用するため、ベースURLをそのまま返す
  const url = new URL(baseUrl)
  return url.toString()
}

const buildExecuteScript = (searchUrl: string, keyword: string, maxItems: number, timeoutMs: number) => `async function run(page) {
  const targetUrl = ${JSON.stringify(searchUrl)};
  const timeoutMs = ${timeoutMs};
  const maxItems = ${maxItems};
  const keyword = ${JSON.stringify(keyword)};

  try {
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
    await page.waitForTimeout(1000);

    // 検索欄を自動検出して入力
    const searchInputSelectors = [
      'input[type="search"]',
      'input[name*="search" i]',
      'input[name="q"]',
      'input[name="query"]',
      'input[placeholder*="search" i]',
      'input[placeholder*="検索" i]',
      'input[id*="search" i]',
      'input[class*="search" i]',
      '#search',
      '.search-input',
    ];

    let searchInput = null;
    for (const selector of searchInputSelectors) {
      searchInput = await page.$(selector);
      if (searchInput) break;
    }

    if (searchInput) {
      // 検索欄にキーワードを入力
      const keywordToSearch = keyword || 'test'; // キーワードがない場合はtestを使用
      await searchInput.fill(keywordToSearch);
      await page.waitForTimeout(500);

      // 検索ボタンを探して実行するか、Enterキーを押す
      const submitSelectors = [
        'button[type="submit"]',
        'input[type="submit"]',
        'button[class*="search" i]',
        'button[id*="search" i]',
      ];

      let submitButton = null;
      for (const selector of submitSelectors) {
        submitButton = await page.$(selector);
        if (submitButton) break;
      }

      if (submitButton) {
        await submitButton.click();
      } else {
        await searchInput.press('Enter');
      }

      await page.waitForTimeout(2000);
    }

    // 検索結果を待つ
    await page.waitForSelector('.search-result, .result, article, [class*="result"]', { timeout: timeoutMs }).catch(() => null);

    const results = await page.evaluate(({ maxItems, targetUrl }) => {
      // 汎用的な検索結果パターンに対応
      const selectors = [
        '.search-result',
        '.search-results article',
        '.result',
        '[class*="searchResult"]',
        '[class*="search-item"]',
        'article',
        '.post',
        '.item',
      ];

      let nodes = [];
      for (const selector of selectors) {
        nodes = Array.from(document.querySelectorAll(selector));
        if (nodes.length > 3) break; // 3件以上ヒットしたパターンを採用
      }

      return nodes.slice(0, maxItems).map((node) => {
        const anchor = node.querySelector('a[href]') || node.querySelector('h1 a, h2 a, h3 a, h4 a');
        const title = node.querySelector('h1, h2, h3, h4, .title, [class*="title"]');
        const description = node.querySelector('.description, .summary, .excerpt, p');

        const href = anchor?.getAttribute('href') ?? '';
        const absoluteUrl = href ? (href.startsWith('http') ? href : new URL(href, targetUrl).href) : '';

        return {
          title: (title?.textContent || anchor?.textContent || '').trim(),
          url: absoluteUrl,
          snippet: (description?.textContent ?? '').replace(/\\s+/g, ' ').trim().substring(0, 300),
        };
      }).filter((item) => item.url && item.title);
    }, { maxItems, targetUrl });

    return { results, searchUrl: page.url() };
  } catch (error) {
    return { error: true, message: error?.message ?? 'Search failed', results: [], searchUrl: targetUrl };
  }
}`
