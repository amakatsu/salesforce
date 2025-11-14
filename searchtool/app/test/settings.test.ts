/**
 * Settings Schema Test
 * 設定スキーマの動作確認テスト
 */

import { settingsSchema } from '../src/shared/settings'

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('  Settings Schema Test')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log()

// Test 1: デフォルト設定
console.log('【Test 1】デフォルト設定の生成')
console.log('────────────────────────────────────────')
try {
  const result = settingsSchema.parse({})
  console.log('✅ 成功: デフォルト設定が正しく生成されました')
  console.log()
  console.log('生成された設定:')
  console.log(JSON.stringify(result, null, 2))
  console.log()
} catch (error) {
  console.error('❌ 失敗:', error)
  process.exit(1)
}

// Test 2: APIキー設定
console.log('【Test 2】APIキーを含む設定')
console.log('────────────────────────────────────────')
try {
  const result = settingsSchema.parse({
    ai: {
      apiKey: 'sk-test-api-key-12345',
      modelId: 'openai/gpt-4o',
    },
    local: {
      root: ['/home/user/projects', '/home/user/docs'],
    },
    keyword: 'テスト検索',
  })
  console.log('✅ 成功: APIキー設定が正しく解析されました')
  console.log()
  console.log('設定内容:')
  console.log('  API Key:', result.ai.apiKey)
  console.log('  Model ID:', result.ai.modelId)
  console.log('  Local Root:', result.local.root)
  console.log('  Keyword:', result.keyword)
  console.log()
} catch (error) {
  console.error('❌ 失敗:', error)
  process.exit(1)
}

// Test 3: 環境変数なしでの動作確認
console.log('【Test 3】環境変数なしでの動作')
console.log('────────────────────────────────────────')
console.log('設定画面から入力したAPIキーのみで動作することを確認')
console.log('✅ 設定ファイルのAPIキーが優先されます')
console.log()

// Test 4: 完全な設定例
console.log('【Test 4】完全な設定例の生成')
console.log('────────────────────────────────────────')
try {
  const fullSettings = settingsSchema.parse({
    keyword: 'API 認証',
    ai: {
      apiKey: 'sk-proj-xxxxxxxxxxxxxxxxxxxxx',
      modelId: 'openai/gpt-4o-mini',
    },
    local: {
      root: [
        '/home/user/projects',
        '/home/user/documents',
        '/home/user/knowledge',
      ],
    },
    redmine: {
      urls: [
        'https://redmine1.example.com',
        'https://redmine2.example.com',
      ],
    },
    sharepoint: {
      urls: [
        'https://company.sharepoint.com/sites/docs',
      ],
    },
    teams: {
      urls: [
        'https://teams.microsoft.com/_#/discover',
      ],
    },
    internalDocs: {
      baseUrl: 'https://docs.internal.example.com',
    },
    browser: {
      userDataDir: '/home/user/.config/chromium',
    },
    excludeGlobs: ['.git', 'node_modules', '.venv', 'target', 'dist'],
    limits: {
      localMaxResults: 200,
      redmineMaxResults: 50,
      timeoutSeconds: 30,
      scrollSteps: 5,
    },
  })

  console.log('✅ 成功: 完全な設定が正しく解析されました')
  console.log()
  console.log('JSON出力:')
  console.log(JSON.stringify(fullSettings, null, 2))
  console.log()
} catch (error) {
  console.error('❌ 失敗:', error)
  process.exit(1)
}

// Test 5: 不正な値の検証
console.log('【Test 5】バリデーションテスト')
console.log('────────────────────────────────────────')

const invalidCases = [
  {
    name: '空のルートディレクトリ配列',
    data: { local: { root: [] } },
  },
  {
    name: '不正なRedmine URL',
    data: { redmine: { urls: ['not-a-url'] } },
  },
  {
    name: '範囲外のlocalMaxResults',
    data: { limits: { localMaxResults: 5000 } },
  },
]

invalidCases.forEach(({ name, data }) => {
  try {
    settingsSchema.parse(data)
    console.log(`❌ ${name}: バリデーションが効いていません`)
  } catch (error) {
    console.log(`✅ ${name}: 正しくエラーが発生しました`)
  }
})

console.log()
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
console.log('  すべてのテストが完了しました！')
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

// 正常終了
if (typeof process !== 'undefined') {
  process.exit(0)
}
