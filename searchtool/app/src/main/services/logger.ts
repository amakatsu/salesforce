import fs from 'node:fs'
import path from 'node:path'

export type LogLevel = 'info' | 'warn' | 'error' | 'debug'

export interface LogEntry {
  timestamp: string
  level: LogLevel
  message: string
  context?: string
  data?: Record<string, any>
}

export class Logger {
  private logDir: string
  private currentLogFile: string | null = null

  constructor(userDataPath: string) {
    this.logDir = path.join(userDataPath, 'logs')
    this.ensureLogDirectory()
  }

  private ensureLogDirectory(): void {
    if (!fs.existsSync(this.logDir)) {
      fs.mkdirSync(this.logDir, { recursive: true })
    }
  }

  private getLogFilePath(): string {
    const today = new Date().toISOString().split('T')[0].replace(/-/g, '')
    const filename = `app-${today}.log`
    return path.join(this.logDir, filename)
  }

  private writeLog(entry: LogEntry): void {
    try {
      const logFile = this.getLogFilePath()
      const line = JSON.stringify(entry) + '\n'
      fs.appendFileSync(logFile, line, 'utf-8')
      this.currentLogFile = logFile
    } catch (error) {
      console.error('Failed to write log:', error)
    }
  }

  log(level: LogLevel, message: string, context?: string, data?: Record<string, any>): void {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      data,
    }
    this.writeLog(entry)
  }

  info(message: string, context?: string, data?: Record<string, any>): void {
    this.log('info', message, context, data)
  }

  warn(message: string, context?: string, data?: Record<string, any>): void {
    this.log('warn', message, context, data)
  }

  error(message: string, context?: string, data?: Record<string, any>): void {
    this.log('error', message, context, data)
  }

  debug(message: string, context?: string, data?: Record<string, any>): void {
    this.log('debug', message, context, data)
  }

  getLogDir(): string {
    return this.logDir
  }

  getCurrentLogFile(): string | null {
    return this.currentLogFile || this.getLogFilePath()
  }
}
