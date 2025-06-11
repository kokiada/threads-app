// メディアファイル検証ユーティリティ

export interface MediaValidationResult {
  isValid: boolean;
  error?: string;
  warnings?: string[];
}

export interface MediaSpecs {
  maxFileSize: number; // bytes
  allowedMimeTypes: string[];
  maxDimensions?: {
    width: number;
    height: number;
  };
  maxDuration?: number; // seconds
}

// Threads APIのメディア仕様
export const THREADS_MEDIA_SPECS = {
  IMAGE: {
    maxFileSize: 8 * 1024 * 1024, // 8MB
    allowedMimeTypes: ['image/jpeg', 'image/png'],
    maxDimensions: {
      width: 1440,
      height: 1440,
    },
  },
  VIDEO: {
    maxFileSize: 1024 * 1024 * 1024, // 1GB
    allowedMimeTypes: ['video/mp4', 'video/quicktime'],
    maxDuration: 300, // 5 minutes
  },
} as const;

/**
 * メディアファイルがThreads APIの仕様に適合するかチェック
 */
export function validateMediaFile(
  file: File | { size: number; type: string; name: string },
  mediaType: 'IMAGE' | 'VIDEO'
): MediaValidationResult {
  const specs = THREADS_MEDIA_SPECS[mediaType];
  const warnings: string[] = [];

  // ファイルサイズチェック
  if (file.size > specs.maxFileSize) {
    return {
      isValid: false,
      error: `ファイルサイズが大きすぎます。最大${formatFileSize(specs.maxFileSize)}まで対応しています。`,
    };
  }

  // MIMEタイプチェック
  if (!specs.allowedMimeTypes.includes(file.type)) {
    return {
      isValid: false,
      error: `サポートされていないファイル形式です。対応形式: ${specs.allowedMimeTypes.join(', ')}`,
    };
  }

  // ファイル名の拡張子チェック
  const fileName = file.name;
  const extension = fileName.toLowerCase().split('.').pop();
  const validExtensions = {
    IMAGE: ['jpg', 'jpeg', 'png'],
    VIDEO: ['mp4', 'mov'],
  };

  if (!extension || !validExtensions[mediaType].includes(extension)) {
    warnings.push(`ファイル拡張子が推奨形式と異なります。推奨: ${validExtensions[mediaType].join(', ')}`);
  }

  // 画像の場合の追加チェック
  if (mediaType === 'IMAGE') {
    // ファイルサイズが小さすぎる場合の警告
    if (file.size < 10 * 1024) { // 10KB
      warnings.push('ファイルサイズが小さいため、画質が低い可能性があります。');
    }
  }

  // 動画の場合の追加チェック
  if (mediaType === 'VIDEO') {
    // ファイルサイズが小さすぎる場合の警告
    if (file.size < 100 * 1024) { // 100KB
      warnings.push('ファイルサイズが小さいため、動画が短いか品質が低い可能性があります。');
    }
  }

  return {
    isValid: true,
    warnings: warnings.length > 0 ? warnings : undefined,
  };
}

/**
 * URLからメディアファイルの情報を取得
 */
export async function validateMediaUrl(url: string, mediaType: 'IMAGE' | 'VIDEO'): Promise<MediaValidationResult> {
  try {
    // URLの基本的な検証
    const urlObj = new URL(url);
    if (!['http:', 'https:'].includes(urlObj.protocol)) {
      return {
        isValid: false,
        error: 'HTTPSまたはHTTPのURLのみサポートされています。',
      };
    }

    // HEAD リクエストでファイル情報を取得
    const response = await fetch(url, { method: 'HEAD' });
    
    if (!response.ok) {
      return {
        isValid: false,
        error: `ファイルにアクセスできません (${response.status}: ${response.statusText})`,
      };
    }

    const contentType = response.headers.get('content-type') || '';
    const contentLength = response.headers.get('content-length');
    const fileSize = contentLength ? parseInt(contentLength, 10) : 0;

    // 仮想ファイルオブジェクトを作成して検証
    const virtualFile = {
      size: fileSize,
      type: contentType,
      name: urlObj.pathname.split('/').pop() || 'unknown',
    };

    return validateMediaFile(virtualFile, mediaType);

  } catch (error) {
    return {
      isValid: false,
      error: `URLの検証中にエラーが発生しました: ${error instanceof Error ? error.message : 'Unknown error'}`,
    };
  }
}

/**
 * 画像の寸法をチェック（ブラウザ環境でのみ動作）
 */
export function validateImageDimensions(file: File): Promise<MediaValidationResult> {
  return new Promise((resolve) => {
    if (typeof window === 'undefined') {
      // サーバーサイドでは寸法チェックをスキップ
      resolve({ isValid: true });
      return;
    }

    const img = new Image();
    
    img.onload = () => {
      const specs = THREADS_MEDIA_SPECS.IMAGE;
      const warnings: string[] = [];

      // 最大寸法チェック
      if (specs.maxDimensions) {
        if (img.width > specs.maxDimensions.width || img.height > specs.maxDimensions.height) {
          resolve({
            isValid: false,
            error: `画像サイズが大きすぎます。最大${specs.maxDimensions.width}x${specs.maxDimensions.height}ピクセルまで対応しています。`,
          });
          return;
        }
      }

      // 最小寸法の推奨チェック
      if (img.width < 320 || img.height < 320) {
        warnings.push('画像サイズが小さいため、表示品質が低下する可能性があります。推奨: 320x320ピクセル以上');
      }

      // アスペクト比チェック
      const aspectRatio = img.width / img.height;
      if (aspectRatio > 4 || aspectRatio < 0.25) {
        warnings.push('極端なアスペクト比の画像は、Threadsで適切に表示されない可能性があります。');
      }

      resolve({
        isValid: true,
        warnings: warnings.length > 0 ? warnings : undefined,
      });
    };

    img.onerror = () => {
      resolve({
        isValid: false,
        error: '画像ファイルが破損しているか、サポートされていない形式です。',
      });
    };

    img.src = URL.createObjectURL(file);
  });
}

/**
 * ファイルサイズを人間が読みやすい形式にフォーマット
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * ファイル拡張子からメディアタイプを判定
 */
export function getMediaTypeFromExtension(filename: string): 'IMAGE' | 'VIDEO' | 'UNKNOWN' {
  const extension = filename.toLowerCase().split('.').pop();
  
  if (!extension) return 'UNKNOWN';

  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
  const videoExtensions = ['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm'];

  if (imageExtensions.includes(extension)) {
    return 'IMAGE';
  } else if (videoExtensions.includes(extension)) {
    return 'VIDEO';
  } else {
    return 'UNKNOWN';
  }
}

/**
 * MIMEタイプからメディアタイプを判定
 */
export function getMediaTypeFromMimeType(mimeType: string): 'IMAGE' | 'VIDEO' | 'UNKNOWN' {
  if (mimeType.startsWith('image/')) {
    return 'IMAGE';
  } else if (mimeType.startsWith('video/')) {
    return 'VIDEO';
  } else {
    return 'UNKNOWN';
  }
}