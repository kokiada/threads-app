// 通知システム

export interface NotificationConfig {
  email?: {
    enabled: boolean;
    recipients: string[];
    smtpConfig?: {
      host: string;
      port: number;
      secure: boolean;
      auth: {
        user: string;
        pass: string;
      };
    };
  };
  webhook?: {
    enabled: boolean;
    url: string;
    secret?: string;
  };
  slack?: {
    enabled: boolean;
    webhookUrl: string;
    channel?: string;
  };
  discord?: {
    enabled: boolean;
    webhookUrl: string;
  };
}

export interface NotificationPayload {
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  data?: any;
  timestamp: string;
  accountName?: string;
  postId?: string;
}

export class NotificationService {
  private config: NotificationConfig;

  constructor(config: NotificationConfig) {
    this.config = config;
  }

  // 通知を送信
  async send(payload: NotificationPayload): Promise<void> {
    const promises: Promise<void>[] = [];

    if (this.config.email?.enabled) {
      promises.push(this.sendEmail(payload));
    }

    if (this.config.webhook?.enabled) {
      promises.push(this.sendWebhook(payload));
    }

    if (this.config.slack?.enabled) {
      promises.push(this.sendSlack(payload));
    }

    if (this.config.discord?.enabled) {
      promises.push(this.sendDiscord(payload));
    }

    // すべての通知を並行して送信
    await Promise.allSettled(promises);
  }

  // メール通知
  private async sendEmail(payload: NotificationPayload): Promise<void> {
    if (!this.config.email?.recipients.length) return;

    try {
      // 実際の実装では nodemailer などを使用
      const emailData = {
        to: this.config.email.recipients.join(','),
        subject: `[Threads投稿マネージャー] ${payload.title}`,
        html: this.formatEmailTemplate(payload),
      };

      // メール送信処理（実装例）
      console.log('Sending email notification:', emailData);
      
      // 実際の実装例:
      // const transporter = nodemailer.createTransporter(this.config.email.smtpConfig);
      // await transporter.sendMail(emailData);
      
    } catch (error) {
      console.error('Email notification failed:', error);
    }
  }

  // Webhook通知
  private async sendWebhook(payload: NotificationPayload): Promise<void> {
    if (!this.config.webhook?.url) return;

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // シークレットが設定されている場合は署名を追加
      if (this.config.webhook.secret) {
        const signature = await this.generateWebhookSignature(payload, this.config.webhook.secret);
        headers['X-Threads-Signature'] = signature;
      }

      const response = await fetch(this.config.webhook.url, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Webhook failed: ${response.status} ${response.statusText}`);
      }

    } catch (error) {
      console.error('Webhook notification failed:', error);
    }
  }

  // Slack通知
  private async sendSlack(payload: NotificationPayload): Promise<void> {
    if (!this.config.slack?.webhookUrl) return;

    try {
      const slackPayload = {
        channel: this.config.slack.channel,
        username: 'Threads投稿マネージャー',
        icon_emoji: this.getSlackEmoji(payload.type),
        attachments: [
          {
            color: this.getSlackColor(payload.type),
            title: payload.title,
            text: payload.message,
            fields: this.formatSlackFields(payload),
            ts: Math.floor(new Date(payload.timestamp).getTime() / 1000),
          },
        ],
      };

      const response = await fetch(this.config.slack.webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(slackPayload),
      });

      if (!response.ok) {
        throw new Error(`Slack notification failed: ${response.status} ${response.statusText}`);
      }

    } catch (error) {
      console.error('Slack notification failed:', error);
    }
  }

  // Discord通知
  private async sendDiscord(payload: NotificationPayload): Promise<void> {
    if (!this.config.discord?.webhookUrl) return;

    try {
      const discordPayload = {
        username: 'Threads投稿マネージャー',
        avatar_url: 'https://example.com/bot-avatar.png',
        embeds: [
          {
            title: payload.title,
            description: payload.message,
            color: this.getDiscordColor(payload.type),
            fields: this.formatDiscordFields(payload),
            timestamp: payload.timestamp,
            footer: {
              text: 'Threads投稿マネージャー',
            },
          },
        ],
      };

      const response = await fetch(this.config.discord.webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(discordPayload),
      });

      if (!response.ok) {
        throw new Error(`Discord notification failed: ${response.status} ${response.statusText}`);
      }

    } catch (error) {
      console.error('Discord notification failed:', error);
    }
  }

  // ヘルパーメソッド
  private formatEmailTemplate(payload: NotificationPayload): string {
    const typeColors = {
      success: '#28a745',
      error: '#dc3545',
      warning: '#ffc107',
      info: '#17a2b8',
    };

    return `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: ${typeColors[payload.type]}; color: white; padding: 20px; text-align: center;">
          <h1 style="margin: 0;">${payload.title}</h1>
        </div>
        <div style="padding: 20px; background: #f8f9fa;">
          <p style="font-size: 16px; line-height: 1.6;">${payload.message}</p>
          ${payload.accountName ? `<p><strong>アカウント:</strong> ${payload.accountName}</p>` : ''}
          ${payload.postId ? `<p><strong>投稿ID:</strong> ${payload.postId}</p>` : ''}
          <p style="color: #6c757d; font-size: 12px;">
            送信時刻: ${new Date(payload.timestamp).toLocaleString('ja-JP')}
          </p>
        </div>
      </div>
    `;
  }

  private getSlackEmoji(type: string): string {
    const emojis = {
      success: ':white_check_mark:',
      error: ':x:',
      warning: ':warning:',
      info: ':information_source:',
    };
    return emojis[type as keyof typeof emojis] || ':robot_face:';
  }

  private getSlackColor(type: string): string {
    const colors = {
      success: 'good',
      error: 'danger',
      warning: 'warning',
      info: '#17a2b8',
    };
    return colors[type as keyof typeof colors] || '#17a2b8';
  }

  private getDiscordColor(type: string): number {
    const colors = {
      success: 0x28a745,
      error: 0xdc3545,
      warning: 0xffc107,
      info: 0x17a2b8,
    };
    return colors[type as keyof typeof colors] || 0x17a2b8;
  }

  private formatSlackFields(payload: NotificationPayload): any[] {
    const fields = [];
    
    if (payload.accountName) {
      fields.push({
        title: 'アカウント',
        value: payload.accountName,
        short: true,
      });
    }

    if (payload.postId) {
      fields.push({
        title: '投稿ID',
        value: payload.postId,
        short: true,
      });
    }

    return fields;
  }

  private formatDiscordFields(payload: NotificationPayload): any[] {
    const fields = [];
    
    if (payload.accountName) {
      fields.push({
        name: 'アカウント',
        value: payload.accountName,
        inline: true,
      });
    }

    if (payload.postId) {
      fields.push({
        name: '投稿ID',
        value: payload.postId,
        inline: true,
      });
    }

    return fields;
  }

  private async generateWebhookSignature(payload: NotificationPayload, secret: string): Promise<string> {
    // HMAC-SHA256 署名の生成
    const crypto = await import('crypto');
    const hmac = crypto.createHmac('sha256', secret);
    hmac.update(JSON.stringify(payload));
    return `sha256=${hmac.digest('hex')}`;
  }
}

// 通知テンプレート
export const NotificationTemplates = {
  postSuccess: (accountName: string, postId: string): NotificationPayload => ({
    type: 'success',
    title: '投稿が完了しました',
    message: `${accountName} への投稿が正常に完了しました。`,
    accountName,
    postId,
    timestamp: new Date().toISOString(),
  }),

  postError: (accountName: string, error: string): NotificationPayload => ({
    type: 'error',
    title: '投稿に失敗しました',
    message: `${accountName} への投稿中にエラーが発生しました: ${error}`,
    accountName,
    timestamp: new Date().toISOString(),
  }),

  scheduleSuccess: (accountName: string, scheduledTime: string): NotificationPayload => ({
    type: 'info',
    title: 'スケジュール投稿が設定されました',
    message: `${accountName} のスケジュール投稿が ${new Date(scheduledTime).toLocaleString('ja-JP')} に設定されました。`,
    accountName,
    timestamp: new Date().toISOString(),
  }),

  tokenExpiry: (accountName: string, expiryDate: string): NotificationPayload => ({
    type: 'warning',
    title: 'トークンの有効期限が近づいています',
    message: `${accountName} のアクセストークンが ${new Date(expiryDate).toLocaleDateString('ja-JP')} に期限切れになります。更新が必要です。`,
    accountName,
    timestamp: new Date().toISOString(),
  }),

  systemError: (error: string): NotificationPayload => ({
    type: 'error',
    title: 'システムエラーが発生しました',
    message: `システムで予期しないエラーが発生しました: ${error}`,
    timestamp: new Date().toISOString(),
  }),
};

// グローバル通知サービスインスタンス
let notificationServiceInstance: NotificationService | null = null;

export function getNotificationService(): NotificationService {
  if (!notificationServiceInstance) {
    // 環境変数から設定を読み込み
    const config: NotificationConfig = {
      email: {
        enabled: process.env.EMAIL_NOTIFICATIONS_ENABLED === 'true',
        recipients: process.env.EMAIL_RECIPIENTS?.split(',') || [],
        smtpConfig: process.env.SMTP_HOST ? {
          host: process.env.SMTP_HOST,
          port: parseInt(process.env.SMTP_PORT || '587'),
          secure: process.env.SMTP_SECURE === 'true',
          auth: {
            user: process.env.SMTP_USER || '',
            pass: process.env.SMTP_PASS || '',
          },
        } : undefined,
      },
      webhook: {
        enabled: process.env.WEBHOOK_NOTIFICATIONS_ENABLED === 'true',
        url: process.env.WEBHOOK_URL || '',
        secret: process.env.WEBHOOK_SECRET,
      },
      slack: {
        enabled: process.env.SLACK_NOTIFICATIONS_ENABLED === 'true',
        webhookUrl: process.env.SLACK_WEBHOOK_URL || '',
        channel: process.env.SLACK_CHANNEL,
      },
      discord: {
        enabled: process.env.DISCORD_NOTIFICATIONS_ENABLED === 'true',
        webhookUrl: process.env.DISCORD_WEBHOOK_URL || '',
      },
    };

    notificationServiceInstance = new NotificationService(config);
  }

  return notificationServiceInstance;
}