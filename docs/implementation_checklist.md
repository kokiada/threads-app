# Threads Auto Poster 実装チェックリスト

## Phase 0: プロジェクトセットアップ ✅

### 環境構築
- [x] Reflexプロジェクトの初期化 (`reflex init`)
- [x] 必要なPythonパッケージのインストール
  - [x] reflex
  - [x] sqlalchemy
  - [x] cryptography
  - [x] apscheduler
  - [x] requests
  - [x] python-dotenv
- [x] requirements.txtの作成
- [x] .envファイルの作成（環境変数設定）
- [x] .gitignoreの設定

### プロジェクト構造
- [x] ディレクトリ構造の作成
  ```
  threads/
  ├── app/
  │   ├── __init__.py
  │   ├── models/
  │   ├── services/
  │   ├── pages/
  │   ├── components/
  │   └── utils/
  ├── docs/
  ├── tests/
  └── .env
  ```

---

## Phase 1: データベース設計・実装 ✅

### データベースモデル定義
- [x] SQLAlchemyのセットアップ
- [x] Base modelの作成
- [x] Accountモデルの実装
  - [x] id (PK, Integer, AutoIncrement)
  - [x] name (String, NotNull)
  - [x] threads_user_id (String, Unique, NotNull)
  - [x] access_token (String, Encrypted)
  - [x] token_expires_at (DateTime)
  - [x] status (Enum: active/inactive)
  - [x] created_at (DateTime, default=now)
  - [x] updated_at (DateTime, onupdate=now)
- [x] PostGroupモデルの実装
  - [x] id (PK)
  - [x] name (String, NotNull)
  - [x] description (Text)
  - [x] created_at (DateTime)
  - [x] updated_at (DateTime)
- [x] Postモデルの実装
  - [x] id (PK)
  - [x] group_id (FK to post_groups)
  - [x] media_type (Enum: TEXT/IMAGE/VIDEO/CAROUSEL)
  - [x] text (String, max 500)
  - [x] media_urls (JSON)
  - [x] created_at (DateTime)
  - [x] updated_at (DateTime)
- [x] AccountGroupモデルの実装（中間テーブル）
  - [x] account_id (FK to accounts)
  - [x] group_id (FK to post_groups)
  - [x] 複合主キー設定
- [x] Scheduleモデルの実装
  - [x] id (PK)
  - [x] account_id (FK to accounts)
  - [x] schedule_type (Enum: FIXED/RANDOM)
  - [x] fixed_times (JSON)
  - [x] random_start_time (Time)
  - [x] random_end_time (Time)
  - [x] random_count (Integer)
  - [x] is_active (Boolean, default=False)
  - [x] created_at (DateTime)
  - [x] updated_at (DateTime)
- [x] PostHistoryモデルの実装
  - [x] id (PK)
  - [x] account_id (FK to accounts)
  - [x] post_id (FK to posts, nullable)
  - [x] threads_media_id (String)
  - [x] posted_at (DateTime)
  - [x] status (Enum: success/failed)
- [x] MetricsCacheモデルの実装
  - [x] id (PK)
  - [x] account_id (FK to accounts)
  - [x] threads_media_id (String, nullable)
  - [x] metric_type (Enum: media/user)
  - [x] metric_data (JSON)
  - [x] fetched_at (DateTime)

### データベース初期化
- [x] データベース接続設定
- [ ] マイグレーション機能の実装（Alembic）
- [ ] 初期マイグレーションファイルの作成
- [ ] テストデータ投入スクリプトの作成

---

## Phase 2: ユーティリティ・共通機能 ✅

### 暗号化ユーティリティ
- [x] cryptographyを使用した暗号化クラスの実装
- [x] encrypt_token関数の実装
- [x] decrypt_token関数の実装
- [x] 環境変数からENCRYPTION_KEYを読み込み

### Threads APIクライアント
- [x] ThreadsAPIClientクラスの作成
- [x] 基本設定（base_url, headers）
- [x] create_media_container メソッド
  - [x] TEXT投稿用
  - [x] IMAGE投稿用
  - [x] VIDEO投稿用
  - [x] CAROUSEL投稿用（アイテム作成）
  - [x] CAROUSEL投稿用（コンテナ作成）
- [x] publish_post メソッド
- [x] get_user_threads メソッド
- [x] get_media_insights メソッド
- [x] get_user_insights メソッド
- [x] refresh_access_token メソッド
- [x] get_publishing_limit メソッド
- [x] エラーハンドリング（HTTPエラー、レート制限）
- [x] 指数関数的バックオフの実装

### バリデーション
- [x] 投稿テキストのバリデーション（500文字以内）
- [x] メディアURLのバリデーション
- [ ] スケジュール時刻のバリデーション
- [ ] アカウント情報のバリデーション

---

## Phase 3: サービス層実装 ✅

### AccountService
- [x] create_account メソッド
  - [x] トークン暗号化
  - [x] DB保存
- [x] get_account メソッド（ID指定）
- [x] get_all_accounts メソッド
  - [x] ページネーション対応
  - [x] ステータスフィルタ
- [x] update_account メソッド
  - [x] トークン更新時の暗号化
- [x] delete_account メソッド
  - [x] 関連データの削除（カスケード）
- [x] toggle_account_status メソッド
- [x] get_accounts_needing_token_refresh メソッド
  - [x] 有効期限7日以内のアカウント取得

### PostGroupService
- [x] create_group メソッド
- [x] get_group メソッド
- [x] get_all_groups メソッド
- [x] update_group メソッド
- [x] delete_group メソッド
- [x] assign_accounts_to_group メソッド
- [x] remove_accounts_from_group メソッド
- [x] get_accounts_by_group メソッド

### PostService
- [x] create_post メソッド
- [x] get_post メソッド
- [x] get_posts_by_group メソッド
- [x] update_post メソッド
- [x] delete_post メソッド
- [x] get_random_post_from_group メソッド

### ScheduleService
- [x] create_schedule メソッド
- [x] get_schedule_by_account メソッド
- [x] update_schedule メソッド
- [x] delete_schedule メソッド
- [x] toggle_schedule_status メソッド
- [x] get_active_schedules メソッド

### PostingService
- [x] post_single メソッド（単一アカウント・単一投稿）
  - [x] メディアコンテナ作成
  - [x] 30秒待機（画像/動画の場合）
  - [x] 投稿公開
  - [x] PostHistory記録
- [x] post_random メソッド（単一アカウント・ランダム投稿）
  - [x] グループからランダム選択
  - [x] post_singleを呼び出し
- [x] post_bulk メソッド（複数アカウント・同一投稿）
  - [x] 並列処理（asyncio）
  - [x] レート制限チェック
  - [x] エラーハンドリング
- [x] check_rate_limit メソッド
  - [x] APIから制限確認
  - [x] 投稿可能かチェック

### MetricsService
- [x] fetch_media_metrics メソッド
  - [x] API呼び出し
  - [x] キャッシュ保存
- [x] fetch_user_metrics メソッド
  - [x] 期間指定対応
  - [x] API呼び出し
  - [x] キャッシュ保存
- [x] get_cached_metrics メソッド
- [x] calculate_growth_rate メソッド
  - [x] フォロワー増加率
  - [x] エンゲージメント率
- [x] get_top_growing_accounts メソッド

### TokenService
- [x] refresh_token メソッド
  - [x] API呼び出し
  - [x] DB更新
- [x] refresh_expiring_tokens メソッド
  - [x] 有効期限近いトークンを一括更新

---

## Phase 4: スケジューラー実装 ✅

### APScheduler設定
- [x] スケジューラーの初期化
- [x] JobStoreの設定（SQLAlchemy）
- [x] Executorの設定

### スケジュールジョブ
- [x] execute_scheduled_post 関数
  - [x] アカウント・グループ取得
  - [x] ランダム投稿実行
  - [x] エラーハンドリング
- [x] token_refresh_job 関数
  - [x] 1日1回実行（毎日午前3時）
  - [x] 有効期限近いトークンをリフレッシュ
- [x] schedule_random_posts 関数
  - [x] ランダム時刻の生成
  - [x] ランダム投稿のスケジュール

### スケジューラー管理
- [x] start_scheduler 関数
- [x] stop_scheduler 関数
- [x] reload_schedules 関数
  - [x] 固定時刻ジョブの登録
  - [x] ランダム時刻ジョブの登録
  - [x] スケジュール変更時に再読み込み
- [x] Reflexアプリ起動時の自動起動

---

## Phase 5: Reflex UI実装 ✅

### 共通コンポーネント
- [x] Sidebarコンポーネント
  - [x] ナビゲーションメニュー
  - [x] アクティブページのハイライト
- [x] Cardコンポーネント（Reflex標準使用）
- [x] Tableコンポーネント（Reflex標準使用）
- [x] Modalコンポーネント（Reflex Dialog使用）

### State管理
- [x] BaseStateクラス（DB接続提供）
- [x] AccountStateクラス
  - [x] accounts リスト
  - [x] load_accounts メソッド
  - [x] add_account メソッド
  - [x] delete_account メソッド
  - [x] toggle_status メソッド
- [x] PostStateクラス
  - [x] groups リスト
  - [x] posts リスト
  - [x] load_groups メソッド
  - [x] add_group メソッド
  - [x] load_posts メソッド
  - [x] add_post メソッド
  - [x] delete_post メソッド

### ページ実装

#### 1. ダッシュボードページ
- [x] ページレイアウト作成
- [x] 全体サマリーカード
  - [x] 総アカウント数
  - [x] 今日の投稿数
  - [x] アクティブなスケジュール数
- [x] 成長アカウントランキング（プレースホルダー）

#### 2. アカウント管理ページ
- [x] ページレイアウト作成
- [x] アカウント一覧テーブル
  - [x] 名前、User ID、ステータス表示
- [x] アカウント追加モーダル
  - [x] フォーム（名前、User ID、アクセストークン）
  - [x] 保存処理
- [x] アカウント削除機能
- [x] ステータス切り替えボタン

#### 3. 投稿管理ページ
- [x] ページレイアウト作成
- [x] グループ一覧（左サイドバー）
  - [x] グループ選択
  - [x] グループ追加ボタン
- [x] 投稿一覧（メインエリア）
  - [x] 選択グループの投稿表示
  - [x] 投稿タイプ別バッジ
  - [x] 投稿追加ボタン
- [x] グループ追加モーダル
  - [x] グループ名、説明
- [x] 投稿追加モーダル
  - [x] メディアタイプ選択
  - [x] テキスト入力
  - [x] メディアURL入力
- [x] 投稿削除機能

#### 4. スケジュール設定ページ
- [x] ページレイアウト作成
- [x] ScheduleState実装
- [x] アカウント選択
- [x] スケジュールタイプ選択（固定/ランダム）
- [x] 固定時刻入力
- [x] ランダム時刻設定
- [x] スケジュール作成機能
- [x] 登録済みスケジュール一覧
- [x] 有効/無効切替機能
- [x] 削除機能
- [x] スケジューラー連携

#### 5. 手動投稿ページ
- [x] ページレイアウト作成
- [x] ManualPostState実装
- [x] アカウント複数選択
- [x] 直接入力タブ
  - [x] メディアタイプ選択
  - [x] テキスト入力
  - [x] メディアURL入力
- [x] テンプレートタブ
  - [x] グループ選択
  - [x] 投稿選択
- [x] 投稿実行機能
- [x] 一括投稿対応
- [x] 結果表示

#### 6. メトリクス分析ページ
- [x] ページレイアウト作成
- [x] MetricsState実装
- [x] 成長ランキング表示
- [x] アカウント選択
- [x] メトリクス取得機能
- [x] メトリクス表示（視聴数、いいね、返信、リポスト、フォロワー）

---

## Phase 6: エラーハンドリング・ロギング ✅

### エラーハンドリング
- [x] カスタム例外クラスの定義
  - [x] ThreadsAPIError
  - [x] RateLimitError
  - [x] TokenExpiredError
  - [x] ValidationError
- [x] サービス層のエラーハンドリング
- [x] APIクライアントのエラーハンドリング

### ロギング
- [x] ロギング設定
  - [x] ファイル出力 (logs/YYYYMMDD.log)
  - [x] コンソール出力
  - [x] ログレベル設定 (INFO/WARNING/ERROR)
- [x] 各サービスへのロガー追加
  - [x] ThreadsAPIClient
  - [x] PostingService
  - [x] Scheduler
- [x] API呼び出しのログ記録
- [x] エラーログの記録
- [x] .gitignoreにlogs/追加

---

## Phase 7: テスト

### ユニットテスト
- [ ] モデルのテスト
- [ ] サービス層のテスト
  - [ ] AccountServiceのテスト
  - [ ] PostServiceのテスト
  - [ ] PostingServiceのテスト
  - [ ] MetricsServiceのテスト
- [ ] ユーティリティのテスト
  - [ ] 暗号化/復号化のテスト
  - [ ] バリデーションのテスト

### 統合テスト
- [ ] Threads API連携のテスト（モック使用）
- [ ] スケジューラーのテスト
- [ ] エンドツーエンドの投稿フローテスト

### 手動テスト
- [ ] 各画面の動作確認
- [ ] 投稿フローの確認
- [ ] スケジュール実行の確認
- [ ] メトリクス取得の確認

---

## Phase 8: デプロイ準備

### 設定ファイル
- [ ] Procfileの作成（Railway用）
- [ ] railway.jsonの作成
- [ ] 環境変数の設定ドキュメント作成

### データベース移行
- [ ] 本番用PostgreSQL設定
- [ ] マイグレーションスクリプトの確認
- [ ] バックアップ戦略の策定

### セキュリティ
- [ ] 環境変数の確認
- [ ] シークレットキーの生成
- [ ] HTTPS設定

### パフォーマンス最適化
- [ ] データベースインデックスの追加
- [ ] クエリ最適化
- [ ] キャッシュ戦略の実装

---

## Phase 9: デプロイ

### Railway デプロイ
- [ ] Railwayアカウント作成
- [ ] プロジェクト作成
- [ ] GitHubリポジトリ連携
- [ ] 環境変数設定
- [ ] PostgreSQLアドオン追加
- [ ] デプロイ実行
- [ ] 動作確認

### モニタリング
- [ ] ログ監視設定
- [ ] エラー通知設定
- [ ] パフォーマンスモニタリング

---

## Phase 10: ドキュメント作成

### 開発ドキュメント
- [ ] README.md
  - [ ] プロジェクト概要
  - [ ] セットアップ手順
  - [ ] 開発環境構築
- [ ] API仕様書
- [ ] データベーススキーマ図
- [ ] アーキテクチャ図

### ユーザードキュメント
- [ ] ユーザーマニュアル
  - [ ] アカウント登録方法
  - [ ] 投稿設定方法
  - [ ] スケジュール設定方法
- [ ] トラブルシューティングガイド
- [ ] FAQ

---

## 優先度別タスク分類

### 🔴 Critical（MVP必須）
- Phase 0: プロジェクトセットアップ
- Phase 1: データベース設計・実装
- Phase 2: ユーティリティ・共通機能
- Phase 3: サービス層実装（AccountService, PostService, PostingService）
- Phase 5: Reflex UI実装（アカウント管理、投稿管理、手動投稿）

### 🟡 High（早期実装推奨）
- Phase 3: サービス層実装（ScheduleService, TokenService）
- Phase 4: スケジューラー実装
- Phase 5: Reflex UI実装（スケジュール設定、ダッシュボード）
- Phase 6: エラーハンドリング・ロギング

### 🟢 Medium（段階的実装）
- Phase 3: サービス層実装（MetricsService）
- Phase 5: Reflex UI実装（メトリクス分析）
- Phase 7: テスト

### 🔵 Low（後回し可）
- Phase 8: デプロイ準備
- Phase 9: デプロイ
- Phase 10: ドキュメント作成

---

## 進捗管理

### 完了基準
各タスクは以下の基準で完了とする：
- コードが実装され、動作確認済み
- 必要なテストが実装済み
- コードレビュー完了
- ドキュメント更新済み

### 見積もり時間（参考）
- Phase 0: 2時間
- Phase 1: 4時間
- Phase 2: 6時間
- Phase 3: 12時間
- Phase 4: 4時間
- Phase 5: 20時間
- Phase 6: 3時間
- Phase 7: 8時間
- Phase 8: 3時間
- Phase 9: 2時間
- Phase 10: 4時間

**合計見積もり**: 約68時間

---

**作成日**: 2025年1月
**最終更新**: 2025年1月
