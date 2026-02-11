import { spawn } from 'node:child_process'
import readline from 'node:readline'

const RG_CANDIDATES = ['rga', 'rg'] as const

export type LocalSearchInput = {
  root: string[]
  query: string
  max: number
  excludeGlobs?: string[]
}

export type LocalSearchHit = {
  path: string
  line: number
  snippet: string
}

export const runLocalSearch = async ({ root, query, max, excludeGlobs = [] }: LocalSearchInput): Promise<LocalSearchHit[]> => {
  if (!root?.length) {
    throw new Error('検索対象のルートディレクトリを設定してください')
  }
  if (!query.trim()) {
    return []
  }
  const binary = await detectBinary()
  const args = ['--json', '-n']
  excludeGlobs.forEach((pattern) => {
    if (!pattern) return
    args.push('--glob', `!${pattern}`)
  })
  args.push('-m', String(max), query, ...root)

  return new Promise((resolve, reject) => {
    const child = spawn(binary, args, { stdio: ['ignore', 'pipe', 'pipe'] })
    const hits: LocalSearchHit[] = []

    if (!child.stdout) {
      reject(new Error('rg stdout not available'))
      return
    }

    const rl = readline.createInterface({ input: child.stdout })
    rl.on('line', (line) => {
      try {
        const parsed = JSON.parse(line)
        if (parsed.type === 'match') {
          hits.push({
            path: parsed.data.path?.text ?? '',
            line: parsed.data.line_number,
            snippet: parsed.data.lines?.text?.trim() ?? '',
          })
        }
      } catch (error) {
        console.error('Failed to parse rg line', error)
      }
    })

    let stderr = ''
    child.stderr?.on('data', (chunk) => {
      stderr += chunk.toString()
    })

    child.on('error', reject)
    child.on('close', (code) => {
      if (code === 0 || code === 1) {
        resolve(hits)
      } else {
        reject(new Error(`rg exited with code ${code}: ${stderr}`))
      }
    })
  })
}

const detectBinary = async (): Promise<string> => {
  for (const candidate of RG_CANDIDATES) {
    try {
      await runWhich(candidate)
      return candidate
    } catch {
      // keep looping
    }
  }
  throw new Error('ripgrep (rg/rga) が見つかりません。PATHを確認してください。')
}

const runWhich = (binary: string) =>
  new Promise<void>((resolve, reject) => {
    const proc = spawn('which', [binary], { stdio: 'ignore' })
    proc.once('error', reject)
    proc.once('close', (code) => {
      if (code === 0) {
        resolve()
      } else {
        reject(new Error(`which ${binary} exited with code ${code}`))
      }
    })
  })
