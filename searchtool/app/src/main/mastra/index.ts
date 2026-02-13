/**
 * Mastra モジュールのエントリポイント。
 *
 * - generateAgentSummary — 既存の検索フロー（searchService から使用中）
 * - runSearchAgent — スナップショットベース適応型
 *
 * 【拡張ポイント】
 * - runSearchAgent が安定したら generateAgentSummary を削除し、searchService の接続先を切り替え
 */

// レガシー検索フロー（searchService.ts が依存中）
export { generateAgentSummary } from './agent-legacy'
export type { AgentSummaryResult } from './agent-legacy'

// スナップショットベース適応型
export { runSearchAgent } from './agent'
export type { SearchAgentResult } from './agent'

// MCP 設定
export { createPlaywrightMcpClient } from './mcp-config'
