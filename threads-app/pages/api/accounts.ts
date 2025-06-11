import { NextApiRequest, NextApiResponse } from 'next';

// アカウント管理用のモックデータベース（実際の実装では外部データベースを使用）
interface Account {
  id: string;
  name: string;
  username: string;
  accessToken: string;
  refreshToken?: string;
  tokenExpiry: string;
  status: 'active' | 'expired' | 'inactive';
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

// メモリ内のモックデータ（実際の実装では永続化ストレージを使用）
let accounts: Account[] = [
  {
    id: '1',
    name: 'アカウント1',
    username: 'account1',
    accessToken: 'mock_token_1',
    tokenExpiry: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(), // 60日後
    status: 'active',
    avatar: '/placeholder.svg?height=40&width=40',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    name: 'アカウント2',
    username: 'account2',
    accessToken: 'mock_token_2',
    tokenExpiry: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
    status: 'active',
    avatar: '/placeholder.svg?height=40&width=40',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

// アカウント管理API
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  switch (req.method) {
    case 'GET':
      // アカウント一覧取得
      const { id } = req.query;
      if (id) {
        const account = accounts.find(acc => acc.id === id);
        if (!account) {
          return res.status(404).json({ error: 'Account not found' });
        }
        res.status(200).json(account);
      } else {
        res.status(200).json(accounts);
      }
      break;
      
    case 'POST':
      // 新しいアカウント追加
      try {
        const { name, username, accessToken, refreshToken } = req.body;
        
        if (!name || !username || !accessToken) {
          return res.status(400).json({ error: 'Missing required fields: name, username, accessToken' });
        }
        
        const newAccount: Account = {
          id: Date.now().toString(),
          name,
          username,
          accessToken,
          refreshToken,
          tokenExpiry: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
          status: 'active',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        
        accounts.push(newAccount);
        res.status(201).json(newAccount);
      } catch (error) {
        res.status(500).json({ error: 'Failed to create account' });
      }
      break;
      
    case 'PUT':
      // アカウント更新
      try {
        const { id } = req.query;
        const updates = req.body;
        
        if (!id) {
          return res.status(400).json({ error: 'Account ID is required' });
        }
        
        const accountIndex = accounts.findIndex(acc => acc.id === id);
        if (accountIndex === -1) {
          return res.status(404).json({ error: 'Account not found' });
        }
        
        accounts[accountIndex] = {
          ...accounts[accountIndex],
          ...updates,
          updatedAt: new Date().toISOString(),
        };
        
        res.status(200).json(accounts[accountIndex]);
      } catch (error) {
        res.status(500).json({ error: 'Failed to update account' });
      }
      break;
      
    case 'DELETE':
      // アカウント削除
      try {
        const { id } = req.query;
        
        if (!id) {
          return res.status(400).json({ error: 'Account ID is required' });
        }
        
        const accountIndex = accounts.findIndex(acc => acc.id === id);
        if (accountIndex === -1) {
          return res.status(404).json({ error: 'Account not found' });
        }
        
        const deletedAccount = accounts.splice(accountIndex, 1)[0];
        res.status(200).json({ message: 'Account deleted successfully', account: deletedAccount });
      } catch (error) {
        res.status(500).json({ error: 'Failed to delete account' });
      }
      break;
      
    default:
      res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}