// スケジュール実行エンジン

import { getDatabase } from './database';

export interface SchedulerConfig {
  checkInterval: number; // チェック間隔（ミリ秒）
  maxRetries: number;
  retryDelay: number;
}

export class PostScheduler {
  private isRunning: boolean = false;
  private intervalId: NodeJS.Timeout | null = null;
  private config: SchedulerConfig;

  constructor(config: SchedulerConfig = {
    checkInterval: 60000, // 1分
    maxRetries: 3,
    retryDelay: 5000, // 5秒
  }) {
    this.config = config;
  }

  // スケジューラーを開始
  start(): void {
    if (this.isRunning) {
      console.log('Scheduler is already running');
      return;
    }

    console.log('Starting post scheduler...');
    this.isRunning = true;
    
    this.intervalId = setInterval(async () => {
      await this.processScheduledPosts();
    }, this.config.checkInterval);
  }

  // スケジューラーを停止
  stop(): void {
    if (!this.isRunning) {
      console.log('Scheduler is not running');
      return;
    }

    console.log('Stopping post scheduler...');
    this.isRunning = false;
    
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  // スケジュール済み投稿を処理
  private async processScheduledPosts(): Promise<void> {
    try {
      const db = getDatabase();
      const pendingPosts = await db.getPendingScheduledPosts();

      console.log(`Processing ${pendingPosts.length} pending posts...`);

      for (const post of pendingPosts) {
        await this.publishScheduledPost(post.id);
      }
    } catch (error) {
      console.error('Error processing scheduled posts:', error);
    }
  }

  // 個別のスケジュール投稿を公開
  private async publishScheduledPost(postId: string): Promise<void> {
    const db = getDatabase();
    
    try {
      const scheduledPost = await db.getScheduledPost(postId);
      if (!scheduledPost) {
        console.error(`Scheduled post ${postId} not found`);
        return;
      }

      // アカウント情報を取得
      const account = await db.getAccount(scheduledPost.accountId);
      if (!account) {
        await db.updateScheduledPost(postId, {
          status: 'failed',
          error: 'Account not found',
        });
        return;
      }

      // Threads APIに投稿
      const result = await this.postToThreadsAPI(account, scheduledPost);
      
      if (result.success) {
        // 成功時の処理
        await db.updateScheduledPost(postId, {
          status: 'published',
        });

        // 投稿履歴に追加
        await db.createPost({
          accountId: account.id,
          accountName: account.name,
          content: scheduledPost.content,
          threadsPostId: result.postId,
          status: 'published',
          publishedAt: new Date().toISOString(),
        });

        console.log(`Successfully published scheduled post ${postId}`);
      } else {
        // 失敗時の処理
        await db.updateScheduledPost(postId, {
          status: 'failed',
          error: result.error,
        });

        console.error(`Failed to publish scheduled post ${postId}:`, result.error);
      }
    } catch (error) {
      console.error(`Error publishing scheduled post ${postId}:`, error);
      
      await db.updateScheduledPost(postId, {
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  // Threads APIに投稿する
  private async postToThreadsAPI(account: any, scheduledPost: any): Promise<{ success: boolean; postId?: string; error?: string }> {
    try {
      // Step 1: メディアコンテナを作成
      const containerData: any = {
        media_type: scheduledPost.content.mediaType,
        access_token: account.accessToken,
      };

      if (scheduledPost.content.text) containerData.text = scheduledPost.content.text;
      if (scheduledPost.content.imageUrl) containerData.image_url = scheduledPost.content.imageUrl;
      if (scheduledPost.content.videoUrl) containerData.video_url = scheduledPost.content.videoUrl;
      if (scheduledPost.content.replyControl) containerData.reply_control = scheduledPost.content.replyControl;

      const containerResponse = await fetch(`https://graph.threads.net/v1.0/${account.username}/threads`, {
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
      const publishResponse = await fetch(`https://graph.threads.net/v1.0/${account.username}/threads_publish`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          creation_id: containerResult.id,
          access_token: account.accessToken,
        }),
      });

      const publishResult = await publishResponse.json();

      if (!publishResponse.ok) {
        throw new Error(publishResult.error?.message || 'Failed to publish post');
      }

      return {
        success: true,
        postId: publishResult.id,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // 手動でスケジュール処理を実行
  async runOnce(): Promise<void> {
    console.log('Running scheduled posts check manually...');
    await this.processScheduledPosts();
  }
}

// グローバルスケジューラーインスタンス
let schedulerInstance: PostScheduler | null = null;

export function getScheduler(): PostScheduler {
  if (!schedulerInstance) {
    schedulerInstance = new PostScheduler();
  }
  return schedulerInstance;
}

// Next.js API用のスケジューラー管理関数
export function startScheduler(): void {
  const scheduler = getScheduler();
  scheduler.start();
}

export function stopScheduler(): void {
  const scheduler = getScheduler();
  scheduler.stop();
}

export async function runSchedulerOnce(): Promise<void> {
  const scheduler = getScheduler();
  await scheduler.runOnce();
}