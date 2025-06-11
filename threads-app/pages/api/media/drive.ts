import { NextApiRequest, NextApiResponse } from 'next';

// Google Drive連携用のAPI（実装例）
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { method } = req;

  switch (method) {
    case 'GET':
      // Google Driveからファイル一覧を取得
      try {
        const { folderId, pageToken, maxResults = 50 } = req.query;
        
        // Google Drive API呼び出し（実際の実装では認証が必要）
        const driveApiUrl = `https://www.googleapis.com/drive/v3/files`;
        const params = new URLSearchParams({
          q: folderId ? `'${folderId}' in parents` : '',
          fields: 'nextPageToken, files(id, name, mimeType, thumbnailLink, webViewLink, size, createdTime)',
          pageSize: maxResults.toString(),
        });

        if (pageToken) {
          params.append('pageToken', pageToken.toString());
        }

        // 実際の実装では認証ヘッダーが必要
        const accessToken = req.headers.authorization?.replace('Bearer ', '');
        if (!accessToken) {
          return res.status(401).json({ error: 'Google Drive access token required' });
        }

        const response = await fetch(`${driveApiUrl}?${params}`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Accept': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Google Drive API error: ${response.statusText}`);
        }

        const data = await response.json();
        
        // メディアファイルのみをフィルタリング
        const mediaFiles = data.files?.filter((file: any) => {
          const mimeType = file.mimeType;
          return mimeType.startsWith('image/') || mimeType.startsWith('video/');
        }) || [];

        res.status(200).json({
          files: mediaFiles,
          nextPageToken: data.nextPageToken,
        });

      } catch (error) {
        console.error('Google Drive API error:', error);
        res.status(500).json({ 
          error: 'Failed to fetch Google Drive files',
          details: error instanceof Error ? error.message : 'Unknown error'
        });
      }
      break;

    case 'POST':
      // Google Driveファイルの公開URLを取得
      try {
        const { fileId } = req.body;
        
        if (!fileId) {
          return res.status(400).json({ error: 'File ID is required' });
        }

        const accessToken = req.headers.authorization?.replace('Bearer ', '');
        if (!accessToken) {
          return res.status(401).json({ error: 'Google Drive access token required' });
        }

        // ファイルを公開設定にする
        const permissionResponse = await fetch(`https://www.googleapis.com/drive/v3/files/${fileId}/permissions`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            role: 'reader',
            type: 'anyone',
          }),
        });

        if (!permissionResponse.ok) {
          throw new Error(`Failed to set file permissions: ${permissionResponse.statusText}`);
        }

        // ファイルの詳細情報を取得
        const fileResponse = await fetch(`https://www.googleapis.com/drive/v3/files/${fileId}?fields=id,name,mimeType,webContentLink,webViewLink,size`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Accept': 'application/json',
          },
        });

        if (!fileResponse.ok) {
          throw new Error(`Failed to get file details: ${fileResponse.statusText}`);
        }

        const fileData = await fileResponse.json();
        
        // 直接アクセス可能なURLを生成
        const publicUrl = `https://drive.google.com/uc?export=view&id=${fileId}`;

        res.status(200).json({
          success: true,
          file: {
            id: fileData.id,
            name: fileData.name,
            mimeType: fileData.mimeType,
            size: fileData.size,
            publicUrl: publicUrl,
            webViewLink: fileData.webViewLink,
          },
        });

      } catch (error) {
        console.error('Google Drive file sharing error:', error);
        res.status(500).json({ 
          error: 'Failed to share Google Drive file',
          details: error instanceof Error ? error.message : 'Unknown error'
        });
      }
      break;

    default:
      res.setHeader('Allow', ['GET', 'POST']);
      res.status(405).end(`Method ${method} Not Allowed`);
  }
}