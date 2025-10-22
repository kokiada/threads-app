# Phase 6: エラーハンドリング・ロギング 完了報告

## 実装日
2025年1月

## 実装内容

### 1. ロギングシステム

#### logger.py (`threads/utils/logger.py`)
- ロガーのセットアップ関数
- ファイルハンドラー（logs/YYYYMMDD.log）
- コンソールハンドラー
- ログフォーマット設定
- ログレベル設定
  - ファイル: INFO以上
  - コンソール: WARNING以上

#### ログ出力先
```
logs/
└── YYYYMMDD.log  # 日付ごとのログファイル
```

### 2. ロギング実装箇所

#### ThreadsAPIClient (`threads/api/threads_client.py`)
- API リクエスト開始ログ
- レート制限警告ログ
- トークン期限切れエラーログ
- API リクエスト成功ログ
- API リクエスト失敗エラーログ
- リトライ情報ログ

#### PostingService (`threads/services/posting_service.py`)
- 投稿開始ログ（アカウント情報含む）
- 投稿成功ログ（media_id含む）
- 投稿失敗エラーログ

#### Scheduler (`threads/scheduler/scheduler.py`)
- スケジューラー起動ログ
- スケジュール投稿実行ログ
- アカウント/スケジュール状態警告ログ
- グループ選択情報ログ
- トークンリフレッシュジョブログ
- エラーログ

### 3. エラーハンドリング

#### 既存のカスタム例外
- ThreadsAPIError: API呼び出しエラー
- RateLimitError: レート制限エラー
- TokenExpiredError: トークン期限切れ
- ValidationError: バリデーションエラー

#### エラーハンドリング実装
- try-exceptブロックによる例外捕捉
- エラーログ記録
- エラーメッセージの返却
- リトライ処理（指数関数的バックオフ）

### 4. .gitignore更新
- logs/ディレクトリを追加
- ログファイルをGit管理対象外に

## ログレベル

### INFO
- API リクエスト開始/成功
- 投稿開始/成功
- スケジューラー起動
- スケジュール投稿実行
- トークンリフレッシュ完了

### WARNING
- レート制限発生
- アカウント/スケジュール無効
- グループ未設定

### ERROR
- API リクエスト失敗
- 投稿失敗
- トークン期限切れ
- スケジュール実行エラー
- トークンリフレッシュエラー

## ログフォーマット

```
YYYY-MM-DD HH:MM:SS - threads - LEVEL - MESSAGE
```

例:
```
2025-01-22 10:30:15 - threads - INFO - API Request: POST 123456/threads
2025-01-22 10:30:16 - threads - INFO - API Request successful: 123456/threads
2025-01-22 10:30:16 - threads - INFO - Post successful for account TestAccount, media_id: 789012
```

## 技術的な特徴

### ファイルローテーション
- 日付ごとにログファイル作成
- 自動的に新しいファイルに切り替え

### マルチハンドラー
- ファイルとコンソールに同時出力
- レベル別の出力先制御

### UTF-8エンコーディング
- 日本語ログメッセージ対応

### グローバルロガー
- アプリケーション全体で共有
- インポートするだけで使用可能

## 使用方法

### ロガーのインポート
```python
from threads.utils.logger import logger

# ログ出力
logger.info("情報メッセージ")
logger.warning("警告メッセージ")
logger.error("エラーメッセージ")
```

### ログファイルの確認
```bash
# 最新のログを表示
tail -f logs/$(date +%Y%m%d).log

# 特定の日付のログを表示
cat logs/20250122.log

# エラーログのみ抽出
grep ERROR logs/20250122.log
```

## 完了確認

- [x] ロギングシステム実装
- [x] ThreadsAPIClientにロギング追加
- [x] PostingServiceにロギング追加
- [x] Schedulerにロギング追加
- [x] エラーハンドリング確認
- [x] .gitignore更新
- [x] チェックリスト更新

## 次のステップ

Phase 6完了により、以下が可能になりました：
- ✅ 全API呼び出しのログ記録
- ✅ 投稿処理のトレース
- ✅ スケジューラー動作の監視
- ✅ エラーの追跡と分析

次の実装候補：
1. **Phase 7: テスト**（推奨）
   - ユニットテスト
   - 統合テスト
   - E2Eテスト

2. **Phase 8: デプロイ準備**
   - Procfile作成
   - 環境変数設定
   - PostgreSQL移行

## 監視とデバッグ

### 本番環境での監視
```bash
# リアルタイムログ監視
tail -f logs/$(date +%Y%m%d).log

# エラー監視
tail -f logs/$(date +%Y%m%d).log | grep ERROR

# 特定アカウントの監視
tail -f logs/$(date +%Y%m%d).log | grep "account_id=123"
```

### デバッグ時の活用
1. ログファイルから問題箇所を特定
2. タイムスタンプで処理の流れを追跡
3. エラーメッセージから原因を分析
4. API呼び出しの成功/失敗を確認

## 注意事項

1. **ログファイルサイズ**: 日次でファイルが分割されるため、定期的な削除推奨
2. **機密情報**: アクセストークンは暗号化されており、ログには出力されない
3. **パフォーマンス**: ログ出力は最小限に抑えているが、大量のAPI呼び出し時は注意
4. **ログレベル**: 本番環境ではINFO、開発環境ではDEBUGに変更可能
