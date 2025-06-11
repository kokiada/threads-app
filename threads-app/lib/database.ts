// データベース操作用のユーティリティライブラリ
// 実際の実装では MongoDB, PostgreSQL, Firebase などを使用

export interface DatabaseConfig {
  type: 'memory' | 'mongodb' | 'postgresql' | 'firebase';
  connectionString?: string;
  options?: any;
}

export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

export interface Account extends BaseEntity {
  name: string;
  username: string;
  accessToken: string;
  refreshToken?: string;
  tokenExpiry: string;
  status: 'active' | 'expired' | 'inactive';
  avatar?: string;
}

export interface Post extends BaseEntity {
  accountId: string;
  accountName: string;
  content: {
    text?: string;
    mediaType: 'TEXT' | 'IMAGE' | 'VIDEO' | 'CAROUSEL';
    imageUrl?: string;
    videoUrl?: string;
    replyControl?: string;
  };
  threadsPostId?: string;
  status: 'draft' | 'published' | 'failed';
  publishedAt?: string;
  error?: string;
}

export interface ScheduledPost extends BaseEntity {
  accountId: string;
  accountName: string;
  content: {
    text?: string;
    mediaType: 'TEXT' | 'IMAGE' | 'VIDEO' | 'CAROUSEL';
    imageUrl?: string;
    videoUrl?: string;
    replyControl?: string;
  };
  scheduledTime: string;
  status: 'pending' | 'published' | 'failed';
  error?: string;
}

// メモリ内データストア（開発用）
class MemoryDataStore {
  private accounts: Account[] = [];
  private posts: Post[] = [];
  private scheduledPosts: ScheduledPost[] = [];

  // アカウント操作
  async getAccounts(): Promise<Account[]> {
    return this.accounts;
  }

  async getAccount(id: string): Promise<Account | null> {
    return this.accounts.find(acc => acc.id === id) || null;
  }

  async createAccount(data: Omit<Account, 'id' | 'createdAt' | 'updatedAt'>): Promise<Account> {
    const account: Account = {
      ...data,
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    this.accounts.push(account);
    return account;
  }

  async updateAccount(id: string, data: Partial<Account>): Promise<Account | null> {
    const index = this.accounts.findIndex(acc => acc.id === id);
    if (index === -1) return null;
    
    this.accounts[index] = {
      ...this.accounts[index],
      ...data,
      updatedAt: new Date().toISOString(),
    };
    return this.accounts[index];
  }

  async deleteAccount(id: string): Promise<boolean> {
    const index = this.accounts.findIndex(acc => acc.id === id);
    if (index === -1) return false;
    
    this.accounts.splice(index, 1);
    return true;
  }

  // 投稿操作
  async getPosts(accountId?: string): Promise<Post[]> {
    if (accountId) {
      return this.posts.filter(post => post.accountId === accountId);
    }
    return this.posts;
  }

  async getPost(id: string): Promise<Post | null> {
    return this.posts.find(post => post.id === id) || null;
  }

  async createPost(data: Omit<Post, 'id' | 'createdAt' | 'updatedAt'>): Promise<Post> {
    const post: Post = {
      ...data,
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    this.posts.push(post);
    return post;
  }

  async updatePost(id: string, data: Partial<Post>): Promise<Post | null> {
    const index = this.posts.findIndex(post => post.id === id);
    if (index === -1) return null;
    
    this.posts[index] = {
      ...this.posts[index],
      ...data,
      updatedAt: new Date().toISOString(),
    };
    return this.posts[index];
  }

  async deletePost(id: string): Promise<boolean> {
    const index = this.posts.findIndex(post => post.id === id);
    if (index === -1) return false;
    
    this.posts.splice(index, 1);
    return true;
  }

  // スケジュール投稿操作
  async getScheduledPosts(accountId?: string, status?: string): Promise<ScheduledPost[]> {
    let filtered = this.scheduledPosts;
    
    if (accountId) {
      filtered = filtered.filter(post => post.accountId === accountId);
    }
    
    if (status) {
      filtered = filtered.filter(post => post.status === status);
    }
    
    return filtered;
  }

  async getScheduledPost(id: string): Promise<ScheduledPost | null> {
    return this.scheduledPosts.find(post => post.id === id) || null;
  }

  async createScheduledPost(data: Omit<ScheduledPost, 'id' | 'createdAt' | 'updatedAt'>): Promise<ScheduledPost> {
    const post: ScheduledPost = {
      ...data,
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    this.scheduledPosts.push(post);
    return post;
  }

  async updateScheduledPost(id: string, data: Partial<ScheduledPost>): Promise<ScheduledPost | null> {
    const index = this.scheduledPosts.findIndex(post => post.id === id);
    if (index === -1) return null;
    
    this.scheduledPosts[index] = {
      ...this.scheduledPosts[index],
      ...data,
      updatedAt: new Date().toISOString(),
    };
    return this.scheduledPosts[index];
  }

  async deleteScheduledPost(id: string): Promise<boolean> {
    const index = this.scheduledPosts.findIndex(post => post.id === id);
    if (index === -1) return false;
    
    this.scheduledPosts.splice(index, 1);
    return true;
  }

  // 期限切れのスケジュール投稿を取得
  async getPendingScheduledPosts(): Promise<ScheduledPost[]> {
    const now = new Date();
    return this.scheduledPosts.filter(post => 
      post.status === 'pending' && new Date(post.scheduledTime) <= now
    );
  }
}

// データベースインスタンス（シングルトン）
let dbInstance: MemoryDataStore | null = null;

export function getDatabase(): MemoryDataStore {
  if (!dbInstance) {
    dbInstance = new MemoryDataStore();
    
    // 初期データの追加
    dbInstance.createAccount({
      name: 'アカウント1',
      username: 'account1',
      accessToken: 'mock_token_1',
      tokenExpiry: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'active',
      avatar: '/placeholder.svg?height=40&width=40',
    });
    
    dbInstance.createAccount({
      name: 'アカウント2',
      username: 'account2',
      accessToken: 'mock_token_2',
      tokenExpiry: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'active',
      avatar: '/placeholder.svg?height=40&width=40',
    });
  }
  
  return dbInstance;
}

// 暗号化ユーティリティ（実際の実装では強力な暗号化ライブラリを使用）
export function encryptToken(token: string): string {
  // 簡易的な暗号化（実際の実装では AES-256 などを使用）
  return Buffer.from(token).toString('base64');
}

export function decryptToken(encryptedToken: string): string {
  // 簡易的な復号化
  return Buffer.from(encryptedToken, 'base64').toString('utf-8');
}