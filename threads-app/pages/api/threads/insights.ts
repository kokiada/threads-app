import { NextApiRequest, NextApiResponse } from 'next';

// Threads API インサイト取得エンドポイント
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    try {
      const { userId, mediaId, accessToken, metric, since, until, breakdown } = req.query;
      
      if (!accessToken) {
        return res.status(400).json({ error: 'Missing required parameter: accessToken' });
      }
      
      let endpoint: string;
      let params: URLSearchParams;
      
      if (mediaId) {
        // メディアインサイト
        endpoint = `https://graph.threads.net/v1.0/${mediaId}/insights`;
        params = new URLSearchParams({
          metric: (metric as string) || 'views,likes,replies,reposts,quotes,shares',
          access_token: accessToken as string,
        });
      } else if (userId) {
        // ユーザーインサイト
        endpoint = `https://graph.threads.net/v1.0/${userId}/threads_insights`;
        params = new URLSearchParams({
          metric: (metric as string) || 'views,likes,replies,reposts,quotes,followers_count',
          access_token: accessToken as string,
        });
        
        if (since) params.append('since', since as string);
        if (until) params.append('until', until as string);
        if (breakdown) params.append('breakdown', breakdown as string);
      } else {
        return res.status(400).json({ error: 'Either userId or mediaId is required' });
      }
      
      const response = await fetch(`${endpoint}?${params.toString()}`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error?.message || 'Failed to fetch insights');
      }
      
      res.status(200).json(data);
      
    } catch (error) {
      console.error('Insights fetch error:', error);
      res.status(500).json({ 
        error: 'Failed to fetch insights',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}