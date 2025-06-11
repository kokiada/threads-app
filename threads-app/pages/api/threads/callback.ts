import { NextApiRequest, NextApiResponse } from 'next';

// Threads API OAuth コールバック処理
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    const { code, error } = req.query;
    
    if (error) {
      return res.status(400).json({ error: 'Authentication failed', details: error });
    }
    
    if (!code) {
      return res.status(400).json({ error: 'Authorization code not provided' });
    }
    
    try {
      // アクセストークンを取得
      const tokenResponse = await fetch('https://graph.threads.net/oauth/access_token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          client_id: process.env.THREADS_CLIENT_ID!,
          client_secret: process.env.THREADS_CLIENT_SECRET!,
          grant_type: 'authorization_code',
          redirect_uri: process.env.THREADS_REDIRECT_URI || 'http://localhost:3000/api/threads/callback',
          code: code as string,
        }),
      });
      
      const tokenData = await tokenResponse.json();
      
      if (!tokenResponse.ok) {
        throw new Error(tokenData.error?.message || 'Failed to get access token');
      }
      
      // 長期トークンに変換
      const longLivedTokenResponse = await fetch('https://graph.threads.net/access_token', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const longLivedTokenData = await longLivedTokenResponse.json();
      
      // トークンを安全に保存（実際の実装では暗号化して保存）
      const accessToken = longLivedTokenData.access_token || tokenData.access_token;
      
      // 成功時のリダイレクト
      res.redirect(`/?auth=success&token=${encodeURIComponent(accessToken)}`);
    } catch (error) {
      console.error('OAuth callback error:', error);
      res.status(500).json({ error: 'Failed to process authentication' });
    }
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}