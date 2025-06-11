// セキュリティユーティリティ

import crypto from 'crypto';

export interface SecurityConfig {
  encryption: {
    algorithm: string;
    keyLength: number;
    ivLength: number;
  };
  rateLimit: {
    windowMs: number;
    maxRequests: number;
  };
  session: {
    secret: string;
    maxAge: number;
  };
}

// デフォルト設定
export const DEFAULT_SECURITY_CONFIG: SecurityConfig = {
  encryption: {
    algorithm: 'aes-256-gcm',
    keyLength: 32,
    ivLength: 16,
  },
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15分
    maxRequests: 100,
  },
  session: {
    secret: process.env.SESSION_SECRET || 'default-secret-change-in-production',
    maxAge: 24 * 60 * 60 * 1000, // 24時間
  },
};

/**
 * 暗号化クラス
 */
export class Encryption {
  private masterKey: Buffer;
  private config: SecurityConfig['encryption'];

  constructor(masterKey: string, config?: SecurityConfig['encryption']) {
    this.masterKey = Buffer.from(masterKey, 'hex');
    this.config = config || DEFAULT_SECURITY_CONFIG.encryption;
  }

  /**
   * データを暗号化
   */
  encrypt(plaintext: string): string {
    try {
      const iv = crypto.randomBytes(this.config.ivLength);
      const cipher = crypto.createCipher(this.config.algorithm, this.masterKey);
      
      let encrypted = cipher.update(plaintext, 'utf8', 'hex');
      encrypted += cipher.final('hex');
      
      const authTag = (cipher as any).getAuthTag?.() || Buffer.alloc(0);
      
      // IV + AuthTag + 暗号化データ
      const result = {
        iv: iv.toString('hex'),
        authTag: authTag.toString('hex'),
        encrypted,
      };
      
      return Buffer.from(JSON.stringify(result)).toString('base64');
    } catch (error) {
      throw new Error(`暗号化に失敗しました: ${error}`);
    }
  }

  /**
   * データを復号化
   */
  decrypt(encryptedData: string): string {
    try {
      const data = JSON.parse(Buffer.from(encryptedData, 'base64').toString());
      
      const iv = Buffer.from(data.iv, 'hex');
      const authTag = Buffer.from(data.authTag, 'hex');
      const encrypted = data.encrypted;
      
      const decipher = crypto.createDecipher(this.config.algorithm, this.masterKey);
      
      if (authTag.length > 0) {
        (decipher as any).setAuthTag(authTag);
      }
      
      let decrypted = decipher.update(encrypted, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      
      return decrypted;
    } catch (error) {
      throw new Error(`復号化に失敗しました: ${error}`);
    }
  }
}

/**
 * ハッシュ化ユーティリティ
 */
export class Hashing {
  /**
   * パスワードをハッシュ化
   */
  static async hashPassword(password: string, saltRounds: number = 12): Promise<string> {
    const bcrypt = await import('bcrypt');
    return bcrypt.hash(password, saltRounds);
  }

  /**
   * パスワードを検証
   */
  static async verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
    const bcrypt = await import('bcrypt');
    return bcrypt.compare(password, hashedPassword);
  }

  /**
   * SHA-256 ハッシュ
   */
  static sha256(data: string): string {
    return crypto.createHash('sha256').update(data).digest('hex');
  }

  /**
   * HMAC-SHA256 署名
   */
  static hmacSha256(data: string, secret: string): string {
    return crypto.createHmac('sha256', secret).update(data).digest('hex');
  }
}

/**
 * レート制限クラス
 */
export class RateLimiter {
  private requests: Map<string, number[]> = new Map();
  private config: SecurityConfig['rateLimit'];

  constructor(config?: SecurityConfig['rateLimit']) {
    this.config = config || DEFAULT_SECURITY_CONFIG.rateLimit;
  }

  /**
   * リクエストをチェック
   */
  checkLimit(identifier: string): { allowed: boolean; resetTime?: Date } {
    const now = Date.now();
    const windowStart = now - this.config.windowMs;
    
    // 古いリクエストを削除
    let userRequests = this.requests.get(identifier) || [];
    userRequests = userRequests.filter(timestamp => timestamp > windowStart);
    
    // リクエスト数をチェック
    if (userRequests.length >= this.config.maxRequests) {
      const resetTime = new Date(userRequests[0] + this.config.windowMs);
      return { allowed: false, resetTime };
    }
    
    // 新しいリクエストを記録
    userRequests.push(now);
    this.requests.set(identifier, userRequests);
    
    return { allowed: true };
  }

  /**
   * 制限をリセット
   */
  resetLimit(identifier: string): void {
    this.requests.delete(identifier);
  }

  /**
   * 全ての制限をクリア
   */
  clearAll(): void {
    this.requests.clear();
  }
}

/**
 * トークン管理
 */
export class TokenManager {
  private encryption: Encryption;

  constructor(encryptionKey: string) {
    this.encryption = new Encryption(encryptionKey);
  }

  /**
   * アクセストークンを暗号化して保存
   */
  encryptToken(token: string): string {
    return this.encryption.encrypt(token);
  }

  /**
   * 暗号化されたトークンを復号化
   */
  decryptToken(encryptedToken: string): string {
    return this.encryption.decrypt(encryptedToken);
  }

  /**
   * JWT風のトークン生成（簡易版）
   */
  generateSessionToken(payload: any, expiresIn: number = 3600): string {
    const header = { typ: 'JWT', alg: 'HS256' };
    const body = {
      ...payload,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + expiresIn,
    };

    const encodedHeader = Buffer.from(JSON.stringify(header)).toString('base64url');
    const encodedBody = Buffer.from(JSON.stringify(body)).toString('base64url');
    const signature = Hashing.hmacSha256(
      `${encodedHeader}.${encodedBody}`,
      process.env.SESSION_SECRET || 'default-secret'
    );

    return `${encodedHeader}.${encodedBody}.${signature}`;
  }

  /**
   * セッショントークンを検証
   */
  verifySessionToken(token: string): { valid: boolean; payload?: any; error?: string } {
    try {
      const [header, body, signature] = token.split('.');
      
      if (!header || !body || !signature) {
        return { valid: false, error: 'Invalid token format' };
      }

      // 署名を検証
      const expectedSignature = Hashing.hmacSha256(
        `${header}.${body}`,
        process.env.SESSION_SECRET || 'default-secret'
      );

      if (signature !== expectedSignature) {
        return { valid: false, error: 'Invalid signature' };
      }

      // ペイロードを復号化
      const payload = JSON.parse(Buffer.from(body, 'base64url').toString());

      // 有効期限をチェック
      if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) {
        return { valid: false, error: 'Token expired' };
      }

      return { valid: true, payload };
    } catch (error) {
      return { valid: false, error: 'Token parsing failed' };
    }
  }
}

/**
 * 入力値検証
 */
export class InputValidator {
  /**
   * SQLインジェクション対策
   */
  static sanitizeSQL(input: string): string {
    return input.replace(/[';\\--]/g, '');
  }

  /**
   * XSS対策
   */
  static sanitizeHTML(input: string): string {
    return input
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;');
  }

  /**
   * メールアドレス検証
   */
  static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * URL検証
   */
  static isValidURL(url: string): boolean {
    try {
      const urlObj = new URL(url);
      return ['http:', 'https:'].includes(urlObj.protocol);
    } catch {
      return false;
    }
  }

  /**
   * パスワード強度チェック
   */
  static checkPasswordStrength(password: string): {
    score: number;
    feedback: string[];
  } {
    const feedback: string[] = [];
    let score = 0;

    if (password.length >= 8) {
      score += 1;
    } else {
      feedback.push('8文字以上にしてください');
    }

    if (/[A-Z]/.test(password)) {
      score += 1;
    } else {
      feedback.push('大文字を含めてください');
    }

    if (/[a-z]/.test(password)) {
      score += 1;
    } else {
      feedback.push('小文字を含めてください');
    }

    if (/\d/.test(password)) {
      score += 1;
    } else {
      feedback.push('数字を含めてください');
    }

    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
      score += 1;
    } else {
      feedback.push('特殊文字を含めてください');
    }

    return { score, feedback };
  }
}

/**
 * セキュリティヘッダー設定
 */
export function getSecurityHeaders(): Record<string, string> {
  return {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https:;",
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  };
}

/**
 * IPアドレス取得
 */
export function getClientIP(req: any): string {
  return (
    req.headers['x-forwarded-for']?.split(',')[0] ||
    req.headers['x-real-ip'] ||
    req.connection?.remoteAddress ||
    req.socket?.remoteAddress ||
    'unknown'
  );
}

/**
 * User-Agent解析
 */
export function parseUserAgent(userAgent: string): {
  browser: string;
  version: string;
  os: string;
  device: string;
} {
  // 簡易的なUser-Agent解析
  const browser = userAgent.includes('Chrome') ? 'Chrome' :
                 userAgent.includes('Firefox') ? 'Firefox' :
                 userAgent.includes('Safari') ? 'Safari' :
                 userAgent.includes('Edge') ? 'Edge' : 'Unknown';

  const os = userAgent.includes('Windows') ? 'Windows' :
            userAgent.includes('Mac') ? 'macOS' :
            userAgent.includes('Linux') ? 'Linux' :
            userAgent.includes('Android') ? 'Android' :
            userAgent.includes('iOS') ? 'iOS' : 'Unknown';

  const device = userAgent.includes('Mobile') ? 'Mobile' :
                userAgent.includes('Tablet') ? 'Tablet' : 'Desktop';

  return {
    browser,
    version: 'Unknown',
    os,
    device,
  };
}

// セキュリティインスタンス
export function createSecurityManager(config?: Partial<SecurityConfig>) {
  const fullConfig = { ...DEFAULT_SECURITY_CONFIG, ...config };
  
  return {
    encryption: new Encryption(
      process.env.ENCRYPTION_KEY || crypto.randomBytes(32).toString('hex'),
      fullConfig.encryption
    ),
    rateLimiter: new RateLimiter(fullConfig.rateLimit),
    tokenManager: new TokenManager(
      process.env.ENCRYPTION_KEY || crypto.randomBytes(32).toString('hex')
    ),
    validator: InputValidator,
    hashing: Hashing,
  };
}