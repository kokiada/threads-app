import { NextApiRequest, NextApiResponse } from 'next';

// Threads API OAuth 2.0 認証エンドポイント
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    // 認証URLを生成
    const clientId = process.env.THREADS_CLIENT_ID;
    const redirectUri = process.env.THREADS_REDIRECT_URI || 'http://localhost:3000/api/threads/callback';
    const scope = 'threads_basic,threads_content_publish,threads_manage_replies,threads_read_replies,threads_manage_insights';
    
    const authUrl = `https://threads.net/oauth/authorize?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${scope}&response_type=code`;
    
    res.status(200).json({ authUrl });
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}