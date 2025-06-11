import { NextApiRequest, NextApiResponse } from 'next';
import { getNotificationService, NotificationTemplates } from '../../lib/notification';

// 通知管理API
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { method } = req;

  switch (method) {
    case 'POST':
      // 通知送信
      try {
        const { type, accountName, postId, error, scheduledTime, expiryDate } = req.body;
        
        if (!type) {
          return res.status(400).json({ error: 'Notification type is required' });
        }

        const notificationService = getNotificationService();
        let payload;

        switch (type) {
          case 'postSuccess':
            if (!accountName || !postId) {
              return res.status(400).json({ error: 'accountName and postId are required for postSuccess' });
            }
            payload = NotificationTemplates.postSuccess(accountName, postId);
            break;

          case 'postError':
            if (!accountName || !error) {
              return res.status(400).json({ error: 'accountName and error are required for postError' });
            }
            payload = NotificationTemplates.postError(accountName, error);
            break;

          case 'scheduleSuccess':
            if (!accountName || !scheduledTime) {
              return res.status(400).json({ error: 'accountName and scheduledTime are required for scheduleSuccess' });
            }
            payload = NotificationTemplates.scheduleSuccess(accountName, scheduledTime);
            break;

          case 'tokenExpiry':
            if (!accountName || !expiryDate) {
              return res.status(400).json({ error: 'accountName and expiryDate are required for tokenExpiry' });
            }
            payload = NotificationTemplates.tokenExpiry(accountName, expiryDate);
            break;

          case 'systemError':
            if (!error) {
              return res.status(400).json({ error: 'error message is required for systemError' });
            }
            payload = NotificationTemplates.systemError(error);
            break;

          default:
            return res.status(400).json({ error: 'Invalid notification type' });
        }

        await notificationService.send(payload);

        res.status(200).json({ 
          success: true,
          message: 'Notification sent successfully',
          type,
        });

      } catch (error) {
        console.error('Notification error:', error);
        res.status(500).json({ 
          error: 'Failed to send notification',
          details: error instanceof Error ? error.message : 'Unknown error'
        });
      }
      break;

    case 'GET':
      // 通知設定の取得
      try {
        const config = {
          email: {
            enabled: process.env.EMAIL_NOTIFICATIONS_ENABLED === 'true',
            recipients: process.env.EMAIL_RECIPIENTS?.split(',') || [],
          },
          webhook: {
            enabled: process.env.WEBHOOK_NOTIFICATIONS_ENABLED === 'true',
            url: process.env.WEBHOOK_URL || '',
          },
          slack: {
            enabled: process.env.SLACK_NOTIFICATIONS_ENABLED === 'true',
            channel: process.env.SLACK_CHANNEL,
          },
          discord: {
            enabled: process.env.DISCORD_NOTIFICATIONS_ENABLED === 'true',
          },
        };

        res.status(200).json(config);
      } catch (error) {
        res.status(500).json({ error: 'Failed to get notification settings' });
      }
      break;

    default:
      res.setHeader('Allow', ['GET', 'POST']);
      res.status(405).end(`Method ${method} Not Allowed`);
  }
}