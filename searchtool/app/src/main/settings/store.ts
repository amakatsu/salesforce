import { promises as fs } from 'node:fs'
import path from 'node:path'
import { AppSettings, defaultSettings, settingsSchema } from '../../shared/settings'

export class SettingsStore {
  private cache: AppSettings = defaultSettings
  private readonly filePath: string

  constructor(userDataDir: string) {
    this.filePath = path.join(userDataDir, 'settings.json')
  }

  async load(): Promise<AppSettings> {
    try {
      const file = await fs.readFile(this.filePath, 'utf-8')
      const parsed = settingsSchema.parse(JSON.parse(file))
      this.cache = parsed
      return parsed
    } catch (error: unknown) {
      const code = (error as NodeJS.ErrnoException).code
      if (code === 'ENOENT' || error instanceof SyntaxError) {
        await this.save(defaultSettings)
        return this.cache
      }
      throw error
    }
  }

  get(): AppSettings {
    return this.cache
  }

  async save(nextSettings: AppSettings): Promise<AppSettings> {
    const parsed = settingsSchema.parse(nextSettings ?? {})
    this.cache = parsed
    await fs.mkdir(path.dirname(this.filePath), { recursive: true })
    await fs.writeFile(this.filePath, JSON.stringify(parsed, null, 2), 'utf-8')
    return this.cache
  }
}
