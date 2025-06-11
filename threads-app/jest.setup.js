// Jest セットアップファイル

// 環境変数の設定
process.env.NODE_ENV = 'test';
process.env.LOG_LEVEL = '3'; // DEBUG
process.env.SESSION_SECRET = 'test-session-secret-key';
process.env.ENCRYPTION_KEY = 'abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890';

// コンソール出力を抑制（テスト中のノイズを減らす）
if (process.env.SUPPRESS_LOGS === 'true') {
  global.console = {
    ...console,
    log: jest.fn(),
    debug: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
  };
}

// グローバルなテストユーティリティ
global.testUtils = {
  // テスト用のモックデータ
  mockAccount: {
    id: 'test-account-1',
    name: 'テストアカウント',
    username: 'test_user',
    accessToken: 'test-access-token',
    refreshToken: 'test-refresh-token',
    tokenExpiry: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
    status: 'active',
    avatar: '/test-avatar.png',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },

  mockPost: {
    id: 'test-post-1',
    accountId: 'test-account-1',
    accountName: 'テストアカウント',
    content: {
      text: 'テスト投稿です',
      mediaType: 'TEXT',
    },
    threadsPostId: 'threads-post-123',
    status: 'published',
    publishedAt: new Date().toISOString(),
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },

  mockScheduledPost: {
    id: 'test-schedule-1',
    accountId: 'test-account-1',
    accountName: 'テストアカウント',
    content: {
      text: 'スケジュール投稿のテストです',
      mediaType: 'TEXT',
    },
    scheduledTime: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    status: 'pending',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },

  // テスト用のHTTPリクエスト作成
  createMockRequest: (method, url, body = {}, headers = {}) => {
    return {
      method,
      url,
      body,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Test Agent',
        ...headers,
      },
      query: {},
      connection: { remoteAddress: '127.0.0.1' },
    };
  },

  // テスト用のHTTPレスポンス作成
  createMockResponse: () => {
    const res = {
      statusCode: 200,
      headers: {},
      _data: '',
      _ended: false,
    };

    res.status = jest.fn((code) => {
      res.statusCode = code;
      return res;
    });

    res.json = jest.fn((data) => {
      res._data = JSON.stringify(data);
      res._ended = true;
      return res;
    });

    res.send = jest.fn((data) => {
      res._data = data;
      res._ended = true;
      return res;
    });

    res.setHeader = jest.fn((key, value) => {
      res.headers[key] = value;
      return res;
    });

    res.end = jest.fn((data) => {
      if (data) res._data = data;
      res._ended = true;
      return res;
    });

    // ヘルパーメソッド
    res._getStatusCode = () => res.statusCode;
    res._getData = () => res._data;
    res._getHeaders = () => res.headers;
    res._isEnded = () => res._ended;

    return res;
  },

  // 非同期処理の待機
  wait: (ms) => new Promise(resolve => setTimeout(resolve, ms)),

  // ランダムな文字列生成
  randomString: (length = 10) => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  },

  // テスト用のトークン生成
  generateTestToken: (payload = {}) => {
    const testPayload = {
      userId: 'test-user-1',
      accountId: 'test-account-1',
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 3600, // 1時間後
      ...payload,
    };

    // 簡易的なJWT風トークン
    const header = Buffer.from(JSON.stringify({ typ: 'JWT', alg: 'HS256' })).toString('base64url');
    const body = Buffer.from(JSON.stringify(testPayload)).toString('base64url');
    const signature = 'test-signature';

    return `${header}.${body}.${signature}`;
  },
};

// モックの設定
jest.mock('node-fetch', () => jest.fn());

// ファイルシステムのモック
jest.mock('fs', () => ({
  existsSync: jest.fn(),
  mkdirSync: jest.fn(),
  unlinkSync: jest.fn(),
  renameSync: jest.fn(),
  promises: {
    appendFile: jest.fn(),
    writeFile: jest.fn(),
    readFile: jest.fn(),
  },
}));

// 暗号化ライブラリのモック
jest.mock('crypto', () => ({
  randomBytes: jest.fn(() => Buffer.from('1234567890abcdef', 'hex')),
  createHash: jest.fn(() => ({
    update: jest.fn().mockReturnThis(),
    digest: jest.fn(() => 'mocked-hash'),
  })),
  createHmac: jest.fn(() => ({
    update: jest.fn().mockReturnThis(),
    digest: jest.fn(() => 'mocked-hmac'),
  })),
  createCipher: jest.fn(() => ({
    update: jest.fn(() => 'encrypted-data'),
    final: jest.fn(() => ''),
    getAuthTag: jest.fn(() => Buffer.from('auth-tag', 'hex')),
  })),
  createDecipher: jest.fn(() => ({
    update: jest.fn(() => 'decrypted-data'),
    final: jest.fn(() => ''),
    setAuthTag: jest.fn(),
  })),
}));

// テストの前後処理
beforeEach(() => {
  // 各テスト前にモックをクリア
  jest.clearAllMocks();
});

afterEach(() => {
  // 各テスト後の清掃
  jest.restoreAllMocks();
});

// 未処理のPromise拒否をキャッチ
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// プロセス終了時の清掃
process.on('exit', () => {
  // 必要に応じて清掃処理を追加
});