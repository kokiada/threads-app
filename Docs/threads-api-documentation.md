# Threads API ドキュメント

本ドキュメントは、Threads APIの使用方法をまとめたものです。

## 概要

Threads APIは、開発者が独自の統合を作成し、クリエイターやブランドがThreadsでの存在感をスケールで管理できるようにするAPIです。

## 前提条件

- Metaアプリの作成が必要
- Threads APIユースケースの設定
- メディアファイルは公開アクセス可能なサーバーでホストする必要がある

## 認証とセットアップ

### 必要な権限

- `threads_basic`: 全エンドポイントで必須
- `threads_content_publish`: 投稿の公開
- `threads_manage_replies`: リプライの管理
- `threads_read_replies`: リプライの読み取り
- `threads_manage_insights`: インサイトの管理

### 認証プロセス

1. OAuth 2.0プロトコルを使用
2. Authorization Windowを実装して認証コードを取得
3. 認証コードを短期アクセストークン（1時間有効）に交換
4. 長期トークン（60日有効）に変換可能

### 重要な注意事項

- Threadsテスターがアプリの権限を付与する必要がある
- アプリユーザーはAuthorization Window経由で認証する必要がある
- 公開プロフィールの権限は90日間持続
- Access Token Debuggerを使用してトークンを検証

## 投稿作成API

### エンドポイント

1. **メディアコンテナ作成**: `POST /{threads-user-id}/threads`
2. **投稿公開**: `POST /{threads-user-id}/threads_publish`

### メディアタイプ

- `TEXT`: テキスト投稿（500文字制限）
- `IMAGE`: 画像投稿
- `VIDEO`: 動画投稿
- `CAROUSEL`: カルーセル投稿（最大20個の画像/動画）

### 主要パラメータ

- `media_type`: メディアタイプ
- `image_url`: 公開画像URL
- `video_url`: 公開動画URL
- `text`: 投稿テキスト
- `is_carousel_item`: カルーセルアイテムかどうか
- `reply_control`: リプライ権限制御
  - `"everyone"`: 全員
  - `"accounts_you_follow"`: フォローしているアカウントのみ
  - `"mentioned_only"`: メンションされたアカウントのみ

### メディア仕様

#### 画像
- 最大8MB
- 320-1440ピクセル幅
- sRGBカラースペース
- JPEG/PNG形式

#### 動画
- MOV/MP4形式
- 最大300秒
- 最大1GBファイルサイズ

### 制限事項

- 24時間あたり250件の投稿制限
- 投稿あたり1つのタグ（#で始まる）
- テキスト投稿にはリンク添付可能

## インサイトAPI

### 必要な権限
- `threads_basic`
- `threads_manage_insights`

### メトリクス

#### メディアインサイト（個別投稿）
- Views（表示数）
- Likes（いいね数）
- Replies（リプライ数）
- Reposts（リポスト数）
- Quotes（引用数）
- Shares（シェア数）

#### ユーザーインサイト
- Views（表示数）
- Likes（いいね数）
- Replies（リプライ数）
- Reposts（リポスト数）
- Quotes（引用数）
- Followers count（フォロワー数）
- Follower demographics（フォロワー属性）

### エンドポイント

- **メディアインサイト**: `/{threads-media-id}/insights`
- **ユーザーインサイト**: `/{threads-user-id}/threads_insights`

### パラメータ

- `metric`: 必須、取得するメトリクスを指定
- `since`、`until`: オプション、時間範囲を定義（デフォルト：2日間）
- `breakdown`: フォロワー属性の詳細（国、都市、年齢、性別）

### 制限事項

- 2024年4月13日以前のメトリクスはサポートされていない
- ネストされたリプライのメトリクスは取得できない
- 2024年6月1日以前のユーザーインサイトは保証されない

## リプライ管理API

### リプライを非表示にする

```bash
curl -X POST \
  -F "hide={true | false}" \
  -F "access_token=<ACCESS_TOKEN>" \
"https://graph.threads.net/v1.0/<THREADS_REPLY_ID>/manage_reply"
```

- トップレベルのリプライを非表示/表示切り替え
- トップレベルのリプライを非表示にすると、ネストされたリプライも自動的に非表示

### リプライ権限制御

投稿作成時に`reply_control`パラメータを使用：

```bash
curl -X POST \
  -F "reply_control=accounts_you_follow" \
  -F "access_token=<ACCESS_TOKEN>" \
"https://graph.threads.net/v1.0/me/threads"
```

## Webhooks

### 目的
特定のトピックやフィールドに関するリアルタイム通知を受信

### 前提条件
- アプリにThreads Webhooksをサブユースケースとして追加する必要がある
- 適切な権限（`threads_basic`、`threads_read_replies`）が必要
- リンクされたビジネスが認証されている必要がある
- メディアオブジェクトの所有者がプライベートアカウントではない

### Webhookフィールド
- `replies`: ユーザーが所有するThreadsメディアへのリプライに関するリアルタイム通知

### Webhookペイロード例

```json
{
    "app_id": "123456",
    "topic": "moderate",
    "values": {
        "value": {
            "id": "8901234",
            "username": "test_username",
            "text": "Reply",
            "permalink": "https://www.threads.net/@test_username/post/Pp"
        }
    }
}
```

### 制限事項
- 完全なリプライWebhook機能には高度なアクセスレベルが必要
- プライベートメディアアカウントのリプライには通知が送信されない

## 実装のヒント

### JavaScript/Node.js での実装

1. **アクセストークンの管理**
   - 短期トークンを長期トークンに変換
   - トークンの有効期限を適切に管理

2. **メディアファイルのアップロード**
   - 画像/動画ファイルを公開アクセス可能なサーバーにアップロード
   - URLを使用してThreads APIに投稿

3. **エラーハンドリング**
   - APIレート制限の処理
   - 認証エラーの適切な処理
   - ネットワークエラーの再試行ロジック

### 推奨フロー

1. アプリの設定とテスターの追加
2. 認証フローの実装
3. 基本的な投稿機能の実装
4. インサイトとリプライ管理の実装
5. Webhookの統合

## 参考リソース

- [Threads API公式ドキュメント](https://developers.facebook.com/docs/threads/)
- [Postman Collection](https://developers.facebook.com/docs/threads/postman-collection)
- [サンプルアプリ](https://developers.facebook.com/docs/threads/sample-app)

## 更新履歴

- 2025-01-06: 初回作成