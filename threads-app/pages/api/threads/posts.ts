import { NextApiRequest, NextApiResponse } from 'next';

interface CreatePostRequest {
  userId: string;
  accessToken: string;
  mediaType: 'TEXT' | 'IMAGE' | 'VIDEO' | 'CAROUSEL';
  text?: string;
  imageUrl?: string;
  videoUrl?: string;
  replyControl?: 'everyone' | 'accounts_you_follow' | 'mentioned_only';
}

// Threads API 投稿作成エンドポイント
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    try {
      const { userId, accessToken, mediaType, text, imageUrl, videoUrl, replyControl }: CreatePostRequest = req.body;
      
      if (!userId || !accessToken) {
        return res.status(400).json({ error: 'Missing required parameters: userId and accessToken' });
      }
      
      // Step 1: メディアコンテナを作成
      const containerData: any = {
        media_type: mediaType,
        access_token: accessToken,
      };
      
      if (text) containerData.text = text;
      if (imageUrl) containerData.image_url = imageUrl;
      if (videoUrl) containerData.video_url = videoUrl;
      if (replyControl) containerData.reply_control = replyControl;
      
      const containerResponse = await fetch(`https://graph.threads.net/v1.0/${userId}/threads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(containerData),
      });
      
      const containerResult = await containerResponse.json();
      
      if (!containerResponse.ok) {
        throw new Error(containerResult.error?.message || 'Failed to create media container');
      }
      
      // Step 2: 投稿を公開
      const publishResponse = await fetch(`https://graph.threads.net/v1.0/${userId}/threads_publish`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          creation_id: containerResult.id,
          access_token: accessToken,
        }),
      });
      
      const publishResult = await publishResponse.json();
      
      if (!publishResponse.ok) {
        throw new Error(publishResult.error?.message || 'Failed to publish post');
      }
      
      res.status(200).json({
        success: true,
        postId: publishResult.id,
        containerId: containerResult.id,
      });
      
    } catch (error) {
      console.error('Post creation error:', error);
      res.status(500).json({ 
        error: 'Failed to create post',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  } else if (req.method === 'GET') {
    // 投稿履歴取得
    try {
      const { userId, accessToken } = req.query;
      
      if (!userId || !accessToken) {
        return res.status(400).json({ error: 'Missing required parameters: userId and accessToken' });
      }
      
      const response = await fetch(`https://graph.threads.net/v1.0/${userId}/threads?fields=id,media_type,media_url,permalink,text,timestamp,username&access_token=${accessToken}`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error?.message || 'Failed to fetch posts');
      }
      
      res.status(200).json(data);
    } catch (error) {
      console.error('Posts fetch error:', error);
      res.status(500).json({ 
        error: 'Failed to fetch posts',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  } else {
    res.setHeader('Allow', ['POST', 'GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}