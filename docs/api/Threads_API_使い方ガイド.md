# Threads API 使い方ガイド

## 概要

Threads APIは、開発者がThreads上でコンテンツを作成・公開し、プロフィール管理やインサイト取得を行うためのAPIです。

## 1. 事前準備

### 必要なもの
- Metaアプリ（Threadsユースケースで作成）
- 公開サーバー（メディアファイルのホスト用）
- Threadsユーザーアクセストークン

### 必要な権限
- `threads_basic` - 全エンドポイントで必須
- `threads_content_publish` - 投稿用
- `threads_manage_replies` - 返信管理用
- `threads_read_replies` - 返信取得用
- `threads_manage_insights` - インサイト取得用

## 2. 認証とアクセストークン

### トークンの種類
| トークン | 有効期間 | 用途 |
|---------|---------|------|
| 短期トークン | 1時間 | 長期トークンとの交換用 |
| 長期トークン | 60日間 | API操作の実行 |

### トークン取得フロー
1. 認証ウィンドウでユーザー認証
2. 認証コードを取得
3. 短期トークンに交換
4. 長期トークンに交換

### 長期トークンのリフレッシュ
```bash
curl -X GET \
  "https://graph.threads.net/refresh_access_token?grant_type=th_refresh_token&refresh_token=<REFRESH_TOKEN>&access_token=<ACCESS_TOKEN>"
```

## 3. 投稿の作成

### 投稿の二段階プロセス
1. **メディアコンテナ作成** - `POST /{threads-user-id}/threads`
2. **投稿公開** - `POST /{threads-user-id}/threads_publish`

### テキスト投稿
```bash
# 1. メディアコンテナ作成
curl -X POST \
  "https://graph.threads.net/v1.0/<THREADS_USER_ID>/threads" \
  -F "media_type=TEXT" \
  -F "text=Hello Threads!" \
  -F "access_token=<ACCESS_TOKEN>"

# 2. 投稿公開
curl -X POST \
  "https://graph.threads.net/v1.0/<THREADS_USER_ID>/threads_publish" \
  -F "creation_id=<MEDIA_CONTAINER_ID>" \
  -F "access_token=<ACCESS_TOKEN>"
```

### 画像投稿
```bash
# 1. メディアコンテナ作成
curl -X POST \
  "https://graph.threads.net/v1.0/<THREADS_USER_ID>/threads" \
  -F "media_type=IMAGE" \
  -F "image_url=https://example.com/image.jpg" \
  -F "text=画像付き投稿" \
  -F "access_token=<ACCESS_TOKEN>"

# 2. 投稿公開（30秒待機後）
curl -X POST \
  "https://graph.threads.net/v1.0/<THREADS_USER_ID>/threads_publish" \
  -F "creation_id=<MEDIA_CONTAINER_ID>" \
  -F "access_token=<ACCESS_TOKEN>"
```

### 動画投稿
```bash
# 1. メディアコンテナ作成
curl -X POST \
  "https://graph.threads.net/v1.0/<THREADS_USER_ID>/threads" \
  -F "media_type=VIDEO" \
  -F "video_url=https://example.com/video.mp4" \
  -F "text=動画投稿" \
  -F "access_token=<ACCESS_TOKEN>"

# 2. 投稿公開
curl -X POST \
  "https://graph.threads.net/v1.0/<THREADS_USER_ID>/threads_publish" \
  -F "creation_id=<MEDIA_CONTAINER_ID>" \
  -F "access_token=<ACCESS_TOKEN>"
```

### カルーセル投稿
```bash
# 1. 各画像のメディアコンテナ作成
curl -X POST \
  "https://graph.threads.net/v1.0/<THREADS_USER_ID>/threads" \
  -F "media_type=IMAGE" \
  -F "image_url=https://example.com/image1.jpg" \
  -F "is_carousel_item=true" \
  -F "access_token=<ACCESS_TOKEN>"

# 2. カルーセルコンテナ作成
curl -X POST \
  "https://graph.threads.net/v1.0/<THREADS_USER_ID>/threads" \
  -F "media_type=CAROUSEL" \
  -F "children=<ITEM1_ID>,<ITEM2_ID>" \
  -F "text=カルーセル投稿" \
  -F "access_token=<ACCESS_TOKEN>"

# 3. 投稿公開
curl -X POST \
  "https://graph.threads.net/v1.0/<THREADS_USER_ID>/threads_publish" \
  -F "creation_id=<CAROUSEL_CONTAINER_ID>" \
  -F "access_token=<ACCESS_TOKEN>"
```

## 4. プロフィール情報の取得

### 自分のプロフィール
```bash
curl -X GET \
  "https://graph.threads.net/v1.0/me?fields=id,username,name,threads_profile_picture_url,threads_biography,is_verified&access_token=<ACCESS_TOKEN>"
```

### 他ユーザーの公開プロフィール
```bash
curl -X GET \
  "https://graph.threads.net/v1.0/profile_lookup?username=<USERNAME>&access_token=<ACCESS_TOKEN>"
```

## 5. 投稿の取得

### ユーザーの投稿一覧
```bash
curl -X GET \
  "https://graph.threads.net/v1.0/<THREADS_USER_ID>/threads?fields=id,media_type,text,timestamp&access_token=<ACCESS_TOKEN>"
```

### 特定の投稿詳細
```bash
curl -X GET \
  "https://graph.threads.net/v1.0/<THREADS_MEDIA_ID>?fields=id,media_type,text,timestamp,username&access_token=<ACCESS_TOKEN>"
```

## 6. インサイトの取得

### 投稿のインサイト
```bash
curl -X GET \
  "https://graph.threads.net/v1.0/<THREADS_MEDIA_ID>/insights?metric=likes,replies,views&access_token=<ACCESS_TOKEN>"
```

### ユーザーのインサイト
```bash
curl -X GET \
  "https://graph.threads.net/v1.0/<THREADS_USER_ID>/threads_insights?metric=views,likes,followers_count&access_token=<ACCESS_TOKEN>"
```

## 7. レート制限

### 制限値
| 操作 | 24時間制限 |
|------|-----------|
| 投稿 | 250件 |
| 返信 | 1,000件 |
| 削除 | 100件 |
| 位置情報検索 | 500件 |

### APIコール数制限
```
コール数 = 4800 × インプレッション数
```

### 制限確認
```bash
curl -X GET \
  "https://graph.threads.net/v1.0/<THREADS_USER_ID>/threads_publishing_limit?fields=quota_usage,config&access_token=<ACCESS_TOKEN>"
```

## 8. メディア仕様

### 画像
- フォーマット: JPEG, PNG
- 最大サイズ: 8MB
- アスペクト比: 10:1まで
- 最小幅: 320px
- 最大幅: 1440px

### 動画
- フォーマット: MOV, MP4
- 最大サイズ: 1GB
- 最大時間: 5分
- 最大解像度: 1920px
- フレームレート: 23-60 FPS

### テキスト
- 最大文字数: 500文字

### カルーセル
- アイテム数: 2-20枚

## 9. エラーハンドリング

### 一般的なHTTPステータスコード
- `200` - 成功
- `400` - リクエストエラー
- `401` - 認証エラー
- `403` - 権限エラー
- `429` - レート制限エラー
- `500` - サーバーエラー

### レート制限エラー対応
1. 指数関数的バックオフを実装
2. クォータ使用量を定期監視
3. 内部キューシステムで投稿を管理

## 10. セキュリティのベストプラクティス

- `client_secret`はサーバーサイドでのみ使用
- アクセストークンの安全な保存
- 定期的なトークンリフレッシュ
- メディアファイルの公開アクセス確保

## 11. 開発のヒント

1. **非同期処理**: 投稿は二段階プロセスのため、適切な待機時間を設ける
2. **エラーハンドリング**: レート制限やメディア処理エラーに対応
3. **監視**: クォータ使用量とAPIレスポンスを監視
4. **テスト**: Threadsテスターアカウントでの事前テスト

## 参考リンク

- [Threads API公式ドキュメント](https://developers.facebook.com/docs/threads)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [アクセストークンデバッガー](https://developers.facebook.com/tools/debug/accesstoken/)