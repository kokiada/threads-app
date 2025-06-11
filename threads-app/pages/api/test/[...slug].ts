import { NextApiRequest, NextApiResponse } from 'next';
import { withSecurity } from '../../../middleware/security';

// テスト用APIエンドポイント（テスト環境セットアップ）
async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { slug } = req.query;
  const testType = Array.isArray(slug) ? slug[0] : slug;

  switch (testType) {
    case 'auth':
      return testAuth(req, res);
    case 'rate-limit':
      return testRateLimit(req, res);
    case 'validation':
      return testValidation(req, res);
    case 'encryption':
      return testEncryption(req, res);
    case 'logging':
      return testLogging(req, res);
    default:
      return res.status(404).json({ error: 'Test not found' });
  }
}

// 認証テスト
async function testAuth(req: NextApiRequest, res: NextApiResponse) {
  const user = (req as any).user;
  
  res.status(200).json({
    message: '認証テスト成功',
    user,
    timestamp: new Date().toISOString(),
  });
}

// レート制限テスト
async function testRateLimit(req: NextApiRequest, res: NextApiResponse) {
  res.status(200).json({
    message: 'レート制限テスト成功',
    timestamp: new Date().toISOString(),
  });
}

// バリデーションテスト
async function testValidation(req: NextApiRequest, res: NextApiResponse) {
  res.status(200).json({
    message: 'バリデーションテスト成功',
    body: req.body,
    timestamp: new Date().toISOString(),
  });
}

// 暗号化テスト
async function testEncryption(req: NextApiRequest, res: NextApiResponse) {
  const { createSecurityManager } = await import('../../../lib/security');
  const security = createSecurityManager();
  
  const testData = 'Hello, World!';
  const encrypted = security.encryption.encrypt(testData);
  const decrypted = security.encryption.decrypt(encrypted);
  
  res.status(200).json({
    message: '暗号化テスト成功',
    original: testData,
    encrypted,
    decrypted,
    match: testData === decrypted,
    timestamp: new Date().toISOString(),
  });
}

// ログテスト
async function testLogging(req: NextApiRequest, res: NextApiResponse) {
  const { getLogger } = await import('../../../lib/logger');
  const logger = getLogger();
  
  logger.info('テストログメッセージ', { test: true }, 'TestAPI');
  logger.warn('テスト警告メッセージ', { test: true }, 'TestAPI');
  logger.error('テストエラーメッセージ', { test: true }, 'TestAPI');
  
  res.status(200).json({
    message: 'ログテスト成功',
    timestamp: new Date().toISOString(),
  });
}

// セキュリティミドルウェアを適用
export default withSecurity(handler, {
  requireAuth: true,
  rateLimit: { maxRequests: 10, windowMs: 60000 },
  inputValidation: {
    required: ['testData'],
    fields: {
      testData: { type: 'string', maxLength: 100 },
    },
  },
});