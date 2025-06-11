// ログシステム

export enum LogLevel {
  ERROR = 0,
  WARN = 1,
  INFO = 2,
  DEBUG = 3,
}

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  data?: any;
  source?: string;
  userId?: string;
  accountId?: string;
  postId?: string;
  error?: Error;
}

export interface LoggerConfig {
  level: LogLevel;
  enableConsole: boolean;
  enableFile: boolean;
  enableDatabase: boolean;
  filePath?: string;
  maxFileSize?: number;
  maxFiles?: number;
}

export class Logger {
  private config: LoggerConfig;
  private logs: LogEntry[] = [];

  constructor(config: LoggerConfig) {
    this.config = config;
  }

  // エラーログ
  error(message: string, data?: any, source?: string, error?: Error): void {
    this.log(LogLevel.ERROR, message, data, source, error);
  }

  // 警告ログ
  warn(message: string, data?: any, source?: string): void {
    this.log(LogLevel.WARN, message, data, source);
  }

  // 情報ログ
  info(message: string, data?: any, source?: string): void {
    this.log(LogLevel.INFO, message, data, source);
  }

  // デバッグログ
  debug(message: string, data?: any, source?: string): void {
    this.log(LogLevel.DEBUG, message, data, source);
  }

  // メインログ処理
  private log(level: LogLevel, message: string, data?: any, source?: string, error?: Error): void {
    if (level > this.config.level) {
      return; // ログレベルが設定より高い場合はスキップ
    }

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      data,
      source,
      error,
    };

    // コンソール出力
    if (this.config.enableConsole) {
      this.logToConsole(entry);
    }

    // ファイル出力
    if (this.config.enableFile) {
      this.logToFile(entry);
    }

    // データベース保存
    if (this.config.enableDatabase) {
      this.logToDatabase(entry);
    }

    // メモリ内ログ（最新1000件まで保持）
    this.logs.push(entry);
    if (this.logs.length > 1000) {
      this.logs.shift();
    }
  }

  // コンソール出力
  private logToConsole(entry: LogEntry): void {
    const levelNames = {
      [LogLevel.ERROR]: 'ERROR',
      [LogLevel.WARN]: 'WARN',
      [LogLevel.INFO]: 'INFO',
      [LogLevel.DEBUG]: 'DEBUG',
    };

    const prefix = `[${entry.timestamp}] [${levelNames[entry.level]}]${entry.source ? ` [${entry.source}]` : ''}`;
    const message = `${prefix} ${entry.message}`;

    switch (entry.level) {
      case LogLevel.ERROR:
        console.error(message, entry.data, entry.error);
        break;
      case LogLevel.WARN:
        console.warn(message, entry.data);
        break;
      case LogLevel.INFO:
        console.info(message, entry.data);
        break;
      case LogLevel.DEBUG:
        console.debug(message, entry.data);
        break;
    }
  }

  // ファイル出力（実際の実装ではファイルシステムへの書き込み）
  private async logToFile(entry: LogEntry): Promise<void> {
    try {
      // 実際の実装では fs を使用してファイルに書き込み
      const logLine = JSON.stringify(entry) + '\n';
      console.log('File log:', logLine); // 開発用
      
      // 実装例:
      // const fs = require('fs').promises;
      // await fs.appendFile(this.config.filePath || 'app.log', logLine);
      
    } catch (error) {
      console.error('Failed to write log to file:', error);
    }
  }

  // データベース保存
  private async logToDatabase(entry: LogEntry): Promise<void> {
    try {
      // 実際の実装ではデータベースに保存
      console.log('Database log:', entry); // 開発用
      
      // 実装例:
      // const db = getDatabase();
      // await db.logs.create(entry);
      
    } catch (error) {
      console.error('Failed to write log to database:', error);
    }
  }

  // ログ取得
  getLogs(filters?: {
    level?: LogLevel;
    source?: string;
    startTime?: string;
    endTime?: string;
    limit?: number;
  }): LogEntry[] {
    let filteredLogs = [...this.logs];

    if (filters) {
      if (filters.level !== undefined) {
        filteredLogs = filteredLogs.filter(log => log.level <= filters.level!);
      }

      if (filters.source) {
        filteredLogs = filteredLogs.filter(log => log.source === filters.source);
      }

      if (filters.startTime) {
        const startTime = new Date(filters.startTime);
        filteredLogs = filteredLogs.filter(log => new Date(log.timestamp) >= startTime);
      }

      if (filters.endTime) {
        const endTime = new Date(filters.endTime);
        filteredLogs = filteredLogs.filter(log => new Date(log.timestamp) <= endTime);
      }

      if (filters.limit) {
        filteredLogs = filteredLogs.slice(-filters.limit);
      }
    }

    return filteredLogs.reverse(); // 最新のログを最初に
  }

  // ログ統計
  getLogStats(): {
    total: number;
    byLevel: Record<string, number>;
    recentErrors: LogEntry[];
  } {
    const byLevel = {
      ERROR: 0,
      WARN: 0,
      INFO: 0,
      DEBUG: 0,
    };

    this.logs.forEach(log => {
      const levelName = LogLevel[log.level] as keyof typeof byLevel;
      byLevel[levelName]++;
    });

    const recentErrors = this.logs
      .filter(log => log.level === LogLevel.ERROR)
      .slice(-10)
      .reverse();

    return {
      total: this.logs.length,
      byLevel,
      recentErrors,
    };
  }

  // ログクリア
  clearLogs(): void {
    this.logs = [];
  }
}

// 特定機能用のロガー
export class PostLogger extends Logger {
  logPostStart(accountName: string, postData: any): void {
    this.info('投稿開始', { accountName, postData }, 'PostService');
  }

  logPostSuccess(accountName: string, postId: string, responseTime: number): void {
    this.info('投稿成功', { accountName, postId, responseTime }, 'PostService');
  }

  logPostError(accountName: string, error: Error, postData: any): void {
    this.error('投稿失敗', { accountName, postData }, 'PostService', error);
  }

  logScheduleSet(accountName: string, scheduledTime: string): void {
    this.info('スケジュール設定', { accountName, scheduledTime }, 'ScheduleService');
  }

  logScheduleExecuted(accountName: string, postId: string): void {
    this.info('スケジュール実行', { accountName, postId }, 'ScheduleService');
  }
}

export class AuthLogger extends Logger {
  logAuthStart(accountName: string): void {
    this.info('認証開始', { accountName }, 'AuthService');
  }

  logAuthSuccess(accountName: string, tokenExpiry: string): void {
    this.info('認証成功', { accountName, tokenExpiry }, 'AuthService');
  }

  logAuthError(accountName: string, error: Error): void {
    this.error('認証失敗', { accountName }, 'AuthService', error);
  }

  logTokenRefresh(accountName: string): void {
    this.info('トークン更新', { accountName }, 'AuthService');
  }

  logTokenExpiry(accountName: string, expiryDate: string): void {
    this.warn('トークン期限切れ', { accountName, expiryDate }, 'AuthService');
  }
}

// グローバルロガーインスタンス
let loggerInstance: Logger | null = null;
let postLoggerInstance: PostLogger | null = null;
let authLoggerInstance: AuthLogger | null = null;

export function getLogger(): Logger {
  if (!loggerInstance) {
    const config: LoggerConfig = {
      level: process.env.LOG_LEVEL ? parseInt(process.env.LOG_LEVEL) : LogLevel.INFO,
      enableConsole: process.env.LOG_CONSOLE !== 'false',
      enableFile: process.env.LOG_FILE === 'true',
      enableDatabase: process.env.LOG_DATABASE === 'true',
      filePath: process.env.LOG_FILE_PATH || 'logs/app.log',
    };

    loggerInstance = new Logger(config);
  }

  return loggerInstance;
}

export function getPostLogger(): PostLogger {
  if (!postLoggerInstance) {
    const config: LoggerConfig = {
      level: LogLevel.INFO,
      enableConsole: true,
      enableFile: true,
      enableDatabase: true,
    };

    postLoggerInstance = new PostLogger(config);
  }

  return postLoggerInstance;
}

export function getAuthLogger(): AuthLogger {
  if (!authLoggerInstance) {
    const config: LoggerConfig = {
      level: LogLevel.INFO,
      enableConsole: true,
      enableFile: true,
      enableDatabase: true,
    };

    authLoggerInstance = new AuthLogger(config);
  }

  return authLoggerInstance;
}

// エラーハンドリングユーティリティ
export function handleApiError(error: any, source: string): { status: number; message: string } {
  const logger = getLogger();

  if (error.name === 'ValidationError') {
    logger.warn('バリデーションエラー', { error: error.message }, source);
    return { status: 400, message: error.message };
  }

  if (error.name === 'UnauthorizedError') {
    logger.warn('認証エラー', { error: error.message }, source);
    return { status: 401, message: '認証が必要です' };
  }

  if (error.name === 'ForbiddenError') {
    logger.warn('認可エラー', { error: error.message }, source);
    return { status: 403, message: 'アクセスが拒否されました' };
  }

  if (error.name === 'NotFoundError') {
    logger.warn('リソースが見つかりません', { error: error.message }, source);
    return { status: 404, message: 'リソースが見つかりません' };
  }

  if (error.name === 'RateLimitError') {
    logger.warn('レート制限エラー', { error: error.message }, source);
    return { status: 429, message: 'リクエストが多すぎます。しばらく待ってから再試行してください' };
  }

  // その他のエラー
  logger.error('予期しないエラー', { error: error.message, stack: error.stack }, source, error);
  return { status: 500, message: 'サーバーエラーが発生しました' };
}