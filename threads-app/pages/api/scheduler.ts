import { NextApiRequest, NextApiResponse } from 'next';
import { getScheduler, startScheduler, stopScheduler, runSchedulerOnce } from '../../lib/scheduler';

// スケジューラー管理API
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { action } = req.query;

  switch (req.method) {
    case 'POST':
      try {
        switch (action) {
          case 'start':
            startScheduler();
            res.status(200).json({ message: 'Scheduler started successfully' });
            break;
            
          case 'stop':
            stopScheduler();
            res.status(200).json({ message: 'Scheduler stopped successfully' });
            break;
            
          case 'run':
            await runSchedulerOnce();
            res.status(200).json({ message: 'Scheduler run completed' });
            break;
            
          default:
            res.status(400).json({ error: 'Invalid action. Use start, stop, or run' });
        }
      } catch (error) {
        console.error('Scheduler action error:', error);
        res.status(500).json({ 
          error: 'Failed to execute scheduler action',
          details: error instanceof Error ? error.message : 'Unknown error'
        });
      }
      break;
      
    case 'GET':
      // スケジューラーの状態を取得
      try {
        const scheduler = getScheduler();
        const isRunning = (scheduler as any).isRunning || false; // プライベートプロパティへのアクセス
        
        res.status(200).json({ 
          isRunning,
          message: isRunning ? 'Scheduler is running' : 'Scheduler is stopped'
        });
      } catch (error) {
        res.status(500).json({ error: 'Failed to get scheduler status' });
      }
      break;
      
    default:
      res.setHeader('Allow', ['GET', 'POST']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}