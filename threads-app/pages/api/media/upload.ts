import { NextApiRequest, NextApiResponse } from 'next';
import formidable from 'formidable';
import fs from 'fs';
import path from 'path';

// メディアファイルアップロード処理
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  try {
    const form = formidable({
      uploadDir: './public/uploads',
      keepExtensions: true,
      maxFileSize: 50 * 1024 * 1024, // 50MB
      maxFiles: 1,
    });

    // アップロードディレクトリを作成
    const uploadDir = './public/uploads';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }

    const [fields, files] = await form.parse(req);
    
    if (!files.media || !files.media[0]) {
      return res.status(400).json({ error: 'ファイルが選択されていません' });
    }

    const file = files.media[0];
    const originalName = file.originalFilename || 'unknown';
    const fileExtension = path.extname(originalName);
    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi'];

    if (!allowedExtensions.includes(fileExtension.toLowerCase())) {
      // アップロードされたファイルを削除
      fs.unlinkSync(file.filepath);
      return res.status(400).json({ 
        error: 'サポートされていないファイル形式です。対応形式: ' + allowedExtensions.join(', ')
      });
    }

    // ファイル名を一意に変更
    const timestamp = Date.now();
    const uniqueFileName = `${timestamp}_${Math.random().toString(36).substring(2)}${fileExtension}`;
    const newFilePath = path.join(uploadDir, uniqueFileName);

    // ファイルを移動
    fs.renameSync(file.filepath, newFilePath);

    // ファイル情報を返却
    const fileInfo = {
      originalName,
      fileName: uniqueFileName,
      filePath: `/uploads/${uniqueFileName}`,
      fileSize: file.size,
      mimeType: file.mimetype,
      uploadedAt: new Date().toISOString(),
    };

    res.status(200).json({
      success: true,
      file: fileInfo,
    });

  } catch (error) {
    console.error('File upload error:', error);
    res.status(500).json({ 
      error: 'ファイルのアップロードに失敗しました',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

// Next.js のデフォルトボディパーサーを無効化
export const config = {
  api: {
    bodyParser: false,
  },
};