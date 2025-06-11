// セキュリティミドルウェア

import { NextApiRequest, NextApiResponse } from 'next';
import { getSecurityHeaders, getClientIP, parseUserAgent, createSecurityManager } from '../lib/security';
import { getLogger } from '../lib/logger';

const security = createSecurityManager();
const logger = getLogger();

/**
 * セキュリティヘッダーを設定するミドルウェア
 */
export function withSecurityHeaders(handler: (req: NextApiRequest, res: NextApiResponse) => Promise<void>) {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    // セキュリティヘッダーを設定
    const headers = getSecurityHeaders();
    Object.entries(headers).forEach(([key, value]) => {
      res.setHeader(key, value);
    });

    return handler(req, res);
  };
}

/**
 * レート制限ミドルウェア
 */
export function withRateLimit(options?: { maxRequests?: number; windowMs?: number }) {
  return function(handler: (req: NextApiRequest, res: NextApiResponse) => Promise<void>) {
    return async (req: NextApiRequest, res: NextApiResponse) => {
      const clientIP = getClientIP(req);
      const identifier = `${clientIP}:${req.url}`;
      
      const { allowed, resetTime } = security.rateLimiter.checkLimit(identifier);
      
      if (!allowed) {
        logger.warn('レート制限に達しました', { 
          ip: clientIP, 
          url: req.url,
          userAgent: req.headers['user-agent'],
          resetTime 
        }, 'RateLimiter');

        res.status(429).json({
          error: 'Too Many Requests',
          message: 'リクエストが多すぎます。しばらく待ってから再試行してください。',
          resetTime: resetTime?.toISOString(),
        });
        return;
      }

      return handler(req, res);
    };
  };
}

/**
 * 認証ミドルウェア
 */
export function withAuth(handler: (req: NextApiRequest, res: NextApiResponse) => Promise<void>) {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    try {
      const authHeader = req.headers.authorization;
      
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        logger.warn('認証ヘッダーが見つかりません', { 
          ip: getClientIP(req),
          url: req.url 
        }, 'AuthMiddleware');

        return res.status(401).json({
          error: 'Unauthorized',
          message: '認証が必要です',
        });
      }

      const token = authHeader.substring(7);
      const { valid, payload, error } = security.tokenManager.verifySessionToken(token);

      if (!valid) {
        logger.warn('無効なトークン', { 
          ip: getClientIP(req),
          url: req.url,
          error 
        }, 'AuthMiddleware');

        return res.status(401).json({
          error: 'Unauthorized',
          message: '無効な認証トークンです',
        });
      }

      // リクエストにユーザー情報を追加
      (req as any).user = payload;

      return handler(req, res);
    } catch (error) {
      logger.error('認証処理エラー', { 
        ip: getClientIP(req),
        url: req.url 
      }, 'AuthMiddleware', error as Error);

      return res.status(500).json({
        error: 'Internal Server Error',
        message: '認証処理中にエラーが発生しました',
      });
    }
  };
}

/**
 * 入力値検証ミドルウェア
 */
export function withInputValidation(schema: any) {
  return function(handler: (req: NextApiRequest, res: NextApiResponse) => Promise<void>) {
    return async (req: NextApiRequest, res: NextApiResponse) => {
      try {
        // 基本的な入力値サニタイズ
        if (req.body && typeof req.body === 'object') {
          req.body = sanitizeObject(req.body);
        }

        if (req.query && typeof req.query === 'object') {
          req.query = sanitizeObject(req.query);
        }

        // スキーマ検証（実際の実装では Joi や Yup などを使用）
        if (schema && req.body) {
          const validationResult = validateWithSchema(req.body, schema);
          if (!validationResult.valid) {
            logger.warn('入力値検証エラー', {
              ip: getClientIP(req),
              url: req.url,
              errors: validationResult.errors
            }, 'InputValidator');

            return res.status(400).json({
              error: 'Validation Error',
              message: '入力値が無効です',
              details: validationResult.errors,
            });
          }
        }

        return handler(req, res);
      } catch (error) {
        logger.error('入力値検証エラー', { 
          ip: getClientIP(req),
          url: req.url 
        }, 'InputValidator', error as Error);

        return res.status(500).json({
          error: 'Internal Server Error',
          message: '入力値検証中にエラーが発生しました',
        });
      }
    };
  };
}

/**
 * ログミドルウェア
 */
export function withLogging(handler: (req: NextApiRequest, res: NextApiResponse) => Promise<void>) {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    const startTime = Date.now();
    const clientIP = getClientIP(req);
    const userAgent = req.headers['user-agent'] || '';
    const userAgentInfo = parseUserAgent(userAgent);

    // リクエスト開始ログ
    logger.info('API リクエスト開始', {
      method: req.method,
      url: req.url,
      ip: clientIP,
      userAgent: userAgentInfo,
      body: req.method === 'POST' ? sanitizeForLogging(req.body) : undefined,
      query: req.query,
    }, 'APIMiddleware');

    // レスポンス終了時にログを出力
    const originalSend = res.send;
    res.send = function(body) {
      const duration = Date.now() - startTime;
      
      logger.info('API リクエスト完了', {
        method: req.method,
        url: req.url,
        ip: clientIP,
        statusCode: res.statusCode,
        duration: `${duration}ms`,
        responseSize: body ? body.length : 0,
      }, 'APIMiddleware');

      return originalSend.call(this, body);
    };

    // エラーハンドリング
    try {
      await handler(req, res);
    } catch (error) {
      const duration = Date.now() - startTime;
      
      logger.error('API リクエストエラー', {
        method: req.method,
        url: req.url,
        ip: clientIP,
        duration: `${duration}ms`,
        error: error instanceof Error ? error.message : 'Unknown error',
      }, 'APIMiddleware', error as Error);

      if (!res.headersSent) {
        res.status(500).json({
          error: 'Internal Server Error',
          message: 'サーバーエラーが発生しました',
        });
      }
    }
  };
}

/**
 * 複数のミドルウェアを組み合わせる関数
 */
export function withSecurity(
  handler: (req: NextApiRequest, res: NextApiResponse) => Promise<void>,
  options?: {
    requireAuth?: boolean;
    rateLimit?: { maxRequests?: number; windowMs?: number };
    inputValidation?: any;
  }
) {
  let wrappedHandler = handler;

  // ログミドルウェア（最外層）
  wrappedHandler = withLogging(wrappedHandler);

  // セキュリティヘッダー
  wrappedHandler = withSecurityHeaders(wrappedHandler);

  // レート制限
  if (options?.rateLimit) {
    wrappedHandler = withRateLimit(options.rateLimit)(wrappedHandler);
  }

  // 入力値検証
  if (options?.inputValidation) {
    wrappedHandler = withInputValidation(options.inputValidation)(wrappedHandler);
  }

  // 認証
  if (options?.requireAuth) {
    wrappedHandler = withAuth(wrappedHandler);
  }

  return wrappedHandler;
}

// ヘルパー関数
function sanitizeObject(obj: any): any {
  if (typeof obj !== 'object' || obj === null) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(sanitizeObject);
  }

  const sanitized: any = {};
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      sanitized[key] = security.validator.sanitizeHTML(value);
    } else if (typeof value === 'object') {
      sanitized[key] = sanitizeObject(value);
    } else {
      sanitized[key] = value;
    }
  }

  return sanitized;
}

function validateWithSchema(data: any, schema: any): { valid: boolean; errors?: string[] } {
  // 簡易的なスキーマ検証（実際の実装では専用ライブラリを使用）
  const errors: string[] = [];

  if (schema.required) {
    for (const field of schema.required) {
      if (!(field in data) || data[field] === undefined || data[field] === null) {
        errors.push(`${field} は必須項目です`);
      }
    }
  }

  if (schema.fields) {
    for (const [field, rules] of Object.entries(schema.fields) as [string, any][]) {
      const value = data[field];
      
      if (value !== undefined && value !== null) {
        if (rules.type === 'string' && typeof value !== 'string') {
          errors.push(`${field} は文字列である必要があります`);
        }
        
        if (rules.type === 'number' && typeof value !== 'number') {
          errors.push(`${field} は数値である必要があります`);
        }
        
        if (rules.maxLength && typeof value === 'string' && value.length > rules.maxLength) {
          errors.push(`${field} は${rules.maxLength}文字以下である必要があります`);
        }
        
        if (rules.pattern && typeof value === 'string' && !new RegExp(rules.pattern).test(value)) {
          errors.push(`${field} の形式が正しくありません`);
        }
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  };
}

function sanitizeForLogging(obj: any): any {
  if (typeof obj !== 'object' || obj === null) {
    return obj;
  }

  const sensitiveFields = ['password', 'token', 'accessToken', 'secret', 'apiKey'];
  const sanitized: any = Array.isArray(obj) ? [] : {};

  for (const [key, value] of Object.entries(obj)) {
    if (sensitiveFields.some(field => key.toLowerCase().includes(field.toLowerCase()))) {
      sanitized[key] = '[REDACTED]';
    } else if (typeof value === 'object') {
      sanitized[key] = sanitizeForLogging(value);
    } else {
      sanitized[key] = value;
    }
  }

  return sanitized;
}