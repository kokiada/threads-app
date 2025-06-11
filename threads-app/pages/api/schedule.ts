import { NextApiRequest, NextApiResponse } from 'next';

interface ScheduledPost {
  id: string;
  accountId: string;
  accountName: string;
  content: {
    text?: string;
    mediaType: 'TEXT' | 'IMAGE' | 'VIDEO' | 'CAROUSEL';
    imageUrl?: string;
    videoUrl?: string;
    replyControl?: 'everyone' | 'accounts_you_follow' | 'mentioned_only';
  };
  scheduledTime: string;
  status: 'pending' | 'published' | 'failed';
  createdAt: string;
  updatedAt: string;
  error?: string;
}

// メモリ内のモックデータ（実際の実装では永続化ストレージを使用）
let scheduledPosts: ScheduledPost[] = [
  {
    id: '1',
    accountId: '1',
    accountName: 'アカウント1',
    content: {
      text: 'スケジュール投稿のテストです',
      mediaType: 'TEXT',
    },
    scheduledTime: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // 24時間後
    status: 'pending',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

// スケジュール管理API
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  switch (req.method) {
    case 'GET':
      // スケジュール一覧取得
      const { id, status, accountId } = req.query;
      
      let filteredPosts = scheduledPosts;
      
      if (id) {
        const post = scheduledPosts.find(p => p.id === id);
        if (!post) {
          return res.status(404).json({ error: 'Scheduled post not found' });
        }
        return res.status(200).json(post);
      }
      
      if (status) {
        filteredPosts = filteredPosts.filter(p => p.status === status);
      }
      
      if (accountId) {
        filteredPosts = filteredPosts.filter(p => p.accountId === accountId);
      }
      
      res.status(200).json(filteredPosts);
      break;
      
    case 'POST':
      // 新しいスケジュール投稿作成
      try {
        const { accountId, accountName, content, scheduledTime } = req.body;
        
        if (!accountId || !accountName || !content || !scheduledTime) {
          return res.status(400).json({ error: 'Missing required fields' });
        }
        
        const newScheduledPost: ScheduledPost = {
          id: Date.now().toString(),
          accountId,
          accountName,
          content,
          scheduledTime,
          status: 'pending',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        
        scheduledPosts.push(newScheduledPost);
        res.status(201).json(newScheduledPost);
      } catch (error) {
        res.status(500).json({ error: 'Failed to create scheduled post' });
      }
      break;
      
    case 'PUT':
      // スケジュール投稿更新
      try {
        const { id } = req.query;
        const updates = req.body;
        
        if (!id) {
          return res.status(400).json({ error: 'Schedule ID is required' });
        }
        
        const postIndex = scheduledPosts.findIndex(p => p.id === id);
        if (postIndex === -1) {
          return res.status(404).json({ error: 'Scheduled post not found' });
        }
        
        scheduledPosts[postIndex] = {
          ...scheduledPosts[postIndex],
          ...updates,
          updatedAt: new Date().toISOString(),
        };
        
        res.status(200).json(scheduledPosts[postIndex]);
      } catch (error) {
        res.status(500).json({ error: 'Failed to update scheduled post' });
      }
      break;
      
    case 'DELETE':
      // スケジュール投稿削除
      try {
        const { id } = req.query;
        
        if (!id) {
          return res.status(400).json({ error: 'Schedule ID is required' });
        }
        
        const postIndex = scheduledPosts.findIndex(p => p.id === id);
        if (postIndex === -1) {
          return res.status(404).json({ error: 'Scheduled post not found' });
        }
        
        const deletedPost = scheduledPosts.splice(postIndex, 1)[0];
        res.status(200).json({ message: 'Scheduled post deleted successfully', post: deletedPost });
      } catch (error) {
        res.status(500).json({ error: 'Failed to delete scheduled post' });
      }
      break;
      
    default:
      res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}