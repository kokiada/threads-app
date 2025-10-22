# Threads Auto Poster プロジェクト引き継ぎ書

## 📋 必読事項

**このドキュメントは実装開始前に必ず全て読んでください。**

---

## 1. プロジェクト概要

### 1.1 プロジェクト名
**Threads Auto Poster**

### 1.2 目的
Threads公式APIを使用して、100以上のアカウントの投稿を自動化・管理するWebアプリケーション

### 1.3 現在のステータス
- **フェーズ**: Phase 0-2 完了、Phase 3 開始前
- **完了済み**: 
  - Phase 0: プロジェクトセットアップ（venv、Reflex初期化、パッケージインストール）
  - Phase 1: データベース設計・実装（全7モデル実装完了）
  - Phase 2: ユーティリティ・共通機能（暗号化、APIクライアント、バリデーション）
- **次のステップ**: Phase 3（サービス層実装）から開始

---

## 2. 重要ドキュメント

### 必読ドキュメント（優先順）
1. **本ドキュメント（handover.md）** - 全体像の把握
2. **[requirements.md](./requirements.md)** - 詳細な要件定義
3. **[implementation_checklist.md](./implementation_checklist.md)** - 実装タスク一覧
4. **[docs/api/](./api/)** - Threads API仕様

### ドキュメント構成
```
docs/
├── handover.md                    # 本ファイル（引き継ぎ書）
├── requirements.md                # 要件定義書
├── implementation_checklist.md    # 実装チェックリスト
└── api/
    ├── threads_api_specification.txt
    ├── Threads_API_使い方ガイド.md
    └── Docs/
        └── インサイト_*.md 等
```

---

## 3. 技術スタック

### 3.1 採用技術
| カテゴリ | 技術 | 理由 |
|---------|------|------|
| 言語 | Python | 要件 |
| フレームワーク | Reflex | サイドメニュー対応、モダンUI、Python純正 |
| データベース | SQLite → PostgreSQL | 初期開発の容易さ、本番移行の柔軟性 |
| ORM | SQLAlchemy | Reflexとの親和性、マイグレーション対応 |
| スケジューラー | APScheduler | Python標準的、永続化対応 |
| 暗号化 | cryptography | トークン暗号化 |
| デプロイ | Railway | 無料枠、DB込み、簡単デプロイ |

### 3.2 主要ライブラリ
```
reflex
sqlalchemy
cryptography
apscheduler
requests
python-dotenv
alembic
```

---

## 4. システムアーキテクチャ

### 4.1 全体構成
```
Reflex WebApp
├── UI層（Reflexコンポーネント）
│   ├── Pages（6画面）
│   ├── Components（共通UI）
│   └── State（状態管理）
│
├── サービス層
│   ├── AccountService
│   ├── PostGroupService
│   ├── PostService
│   ├── ScheduleService
│   ├── PostingService
│   ├── MetricsService
│   └── TokenService
│
├── インフラ層
│   ├── ThreadsAPIClient
│   ├── Database（SQLAlchemy）
│   └── Scheduler（APScheduler）
│
└── ユーティリティ
    ├── 暗号化
    ├── バリデーション
    └── エラーハンドリング
```

### 4.2 ディレクトリ構造
```
threads/
├── threads/                 # メインアプリケーション
│   ├── __init__.py
│   ├── threads.py          # Reflexアプリエントリーポイント
│   ├── models/             # SQLAlchemyモデル
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── account.py
│   │   ├── post_group.py
│   │   ├── post.py
│   │   ├── account_group.py
│   │   ├── schedule.py
│   │   ├── post_history.py
│   │   └── metrics_cache.py
│   ├── services/           # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── account_service.py
│   │   ├── post_group_service.py
│   │   ├── post_service.py
│   │   ├── schedule_service.py
│   │   ├── posting_service.py
│   │   ├── metrics_service.py
│   │   └── token_service.py
│   ├── api/                # 外部API連携
│   │   ├── __init__.py
│   │   └── threads_client.py
│   ├── scheduler/          # スケジューラー
│   │   └── __init__.py
│   ├── pages/              # Reflexページ
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── accounts.py
│   │   ├── posts.py
│   │   ├── schedules.py
│   │   ├── manual_post.py
│   │   └── metrics.py
│   ├── states/             # Reflex State管理
│   │   ├── __init__.py
│   │   ├── base_state.py
│   │   ├── account_state.py
│   │   └── post_state.py
│   ├── components/         # 共通コンポーネント
│   │   ├── __init__.py
│   │   └── sidebar.py
│   └── utils/              # ユーティリティ
│       ├── __init__.py
│       ├── crypto.py
│       ├── validators.py
│       └── exceptions.py
├── scripts/                # 開発・テスト用スクリプト
│   ├── README.md
│   ├── init_db.py
│   ├── test_setup.py
│   └── test_services.py
├── docs/                   # ドキュメント
│   ├── handover.md
│   ├── requirements.md
│   ├── implementation_checklist.md
│   ├── how_to_run.md
│   └── api/
├── tests/                  # テスト
│   └── __init__.py
├── .env                    # 環境変数（gitignore）
├── .env.example
├── .gitignore
├── requirements.txt
├── rxconfig.py
└── threads.db              # SQLiteデータベース
```

---

## 5. データベース設計

### 5.1 主要テーブル
1. **accounts** - アカウント情報（暗号化トークン含む）
2. **post_groups** - 投稿グループ
3. **posts** - 投稿テンプレート
4. **account_groups** - アカウント-グループ紐付け（中間テーブル）
5. **schedules** - スケジュール設定
6. **post_history** - 投稿履歴
7. **metrics_cache** - メトリクスキャッシュ

### 5.2 重要な設計ポイント
- **トークン暗号化**: accountsテーブルのaccess_tokenは必ず暗号化して保存
- **リレーション**: 1グループ → 複数アカウント（1対多）
- **JSON型**: fixed_times, media_urls, metric_dataはJSON型で保存
- **インデックス**: threads_user_id, account_id, group_idにインデックス必須

詳細は[requirements.md](./requirements.md)の「4.2 データベース設計」参照

---

## 6. Threads API連携の重要ポイント

### 6.1 投稿の二段階プロセス
**必ず守ること**: 投稿は以下の2ステップで実行

1. **メディアコンテナ作成**: `POST /{threads-user-id}/threads`
2. **30秒待機**（画像/動画の場合）
3. **投稿公開**: `POST /{threads-user-id}/threads_publish`

### 6.2 レート制限
- **投稿制限**: 250件/24時間（アカウント単位）
- **APIコール制限**: 4800 × インプレッション数
- **対策**: 投稿前に`threads_publishing_limit`エンドポイントで確認

### 6.3 トークン管理
- **短期トークン**: 1時間有効（長期トークンへの交換用）
- **長期トークン**: 60日間有効（自動リフレッシュ必須）
- **リフレッシュ**: 有効期限7日前に自動実行推奨

### 6.4 取得可能なメトリクス
**投稿別**: views, likes, replies, reposts, quotes, shares
**ユーザー別**: views, likes, replies, reposts, quotes, clicks, followers_count, follower_demographics

詳細は[docs/api/Threads_API_使い方ガイド.md](./api/Threads_API_使い方ガイド.md)参照

---

## 7. 実装の進め方

### 7.1 推奨実装順序
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 5（UI） → Phase 4 → Phase 6 → Phase 7

**理由**: 
- データベース基盤を先に構築
- サービス層を実装してからUI実装
- スケジューラーは基本機能完成後

### 7.2 MVP（最小機能）の範囲
以下を最優先で実装：
- [ ] アカウント管理（CRUD）
- [ ] 投稿グループ管理
- [ ] 単一投稿機能（手動）
- [ ] 基本的なUI（アカウント管理、投稿管理、手動投稿画面）

### 7.3 チェックリストの使い方
[implementation_checklist.md](./implementation_checklist.md)を参照し、以下のルールで進める：

1. 各タスクを上から順に実装
2. 完了したら`- [ ]`を`- [x]`に変更
3. 優先度マーク（🔴🟡🟢🔵）を参考に調整可能
4. 各Phaseの完了基準を満たしてから次へ

---

## 8. 重要な実装上の注意点

### 8.1 セキュリティ
- **トークン暗号化**: cryptographyのFernetを使用
- **環境変数**: client_secret, ENCRYPTION_KEYは.envで管理
- **.gitignore**: .env, *.db, __pycache__を必ず追加

### 8.2 エラーハンドリング
- **指数関数的バックオフ**: レート制限エラー時に実装必須
- **カスタム例外**: ThreadsAPIError, RateLimitError等を定義
- **ロギング**: 全API呼び出しをログ記録

### 8.3 非同期処理
- **投稿処理**: 30秒待機はasyncio.sleepを使用
- **一括投稿**: asyncioで並列処理
- **メトリクス取得**: バックグラウンドで実行

### 8.4 Reflex特有の注意点
- **State管理**: 各ページごとにStateクラスを作成
- **イベントハンドラー**: Stateメソッドとして実装
- **非同期処理**: Reflexのイベントハンドラーは同期/非同期両対応
- **Setterメソッド**: Reflex 0.8.9以降は明示的にsetterを定義する必要あり
- **条件分岐**: Pythonの`if`ではなく`rx.cond`を使用

---

## 9. 開発環境セットアップ

### 9.1 初回セットアップ手順
```bash
# 1. リポジトリクローン
git clone https://github.com/kokiada/threads-app.git
cd threads-app

# 2. 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. パッケージインストール
pip install -r requirements.txt

# 4. .env作成
cp .env.example .env
# ENCRYPTION_KEYを生成して設定
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# 生成されたキーを.envのENCRYPTION_KEYに設定

# 5. データベース初期化
python scripts/init_db.py

# 6. 動作確認テスト
python scripts/test_setup.py
```

### 9.2 venv使用時の重要な注意点

**プロジェクトパス**: `/home/koki/work/threads`

#### Pythonコマンド実行時
venv環境でPythonスクリプトを実行する際は、必ず**フルパス**を使用してください：

```bash
# ✅ 正しい方法
/home/koki/work/threads/venv/bin/python scripts/test_setup.py
/home/koki/work/threads/venv/bin/python scripts/test_scheduler.py

# ❌ 動作しない方法
python scripts/test_setup.py
./venv/bin/python scripts/test_setup.py
source venv/bin/activate && python scripts/test_setup.py
```

#### Reflexアプリ起動時
```bash
# ✅ 正しい方法
/home/koki/work/threads/venv/bin/reflex run

# または、カレントディレクトリが /home/koki/work/threads の場合
reflex run  # venvがアクティブな場合
```

#### パッケージインストール時
```bash
# ✅ 正しい方法
/home/koki/work/threads/venv/bin/pip install <package-name>

# requirements.txt更新時
/home/koki/work/threads/venv/bin/pip freeze > requirements.txt
```

#### 理由
- Linux環境では`source`コマンドが使用できない場合がある
- 相対パス（`./venv/bin/python`）が認識されない環境がある
- フルパス指定により確実にvenv環境のPythonを使用できる

### 9.3 環境変数設定（.env）
```env
DATABASE_URL=sqlite:///./threads.db
ENCRYPTION_KEY=<Fernetで生成したキー>
THREADS_APP_ID=<ThreadsアプリID>
THREADS_APP_SECRET=<ThreadsアプリSecret>
```

**重要**: 
- ENCRYPTION_KEYは必ず生成すること（上記セットアップ手順参照）
- .envファイルは.gitignoreに含まれているため、Gitにコミットされない
- 本番環境では環境変数として設定すること

### 9.4 開発サーバー起動
```bash
reflex run
```

**アクセス**: http://localhost:3000

**利用可能なページ**:
- ダッシュボード: `/`
- アカウント管理: `/accounts`
- 投稿管理: `/posts`
- スケジュール設定: `/schedules`
- 手動投稿: `/manual-post`
- メトリクス分析: `/metrics`

---

## 10. テスト戦略

### 10.1 テスト方針
- **ユニットテスト**: サービス層、ユーティリティ
- **統合テスト**: API連携（モック使用）
- **手動テスト**: UI動作確認

### 10.2 テストツール
- pytest
- pytest-asyncio
- unittest.mock（API呼び出しのモック）

---

## 11. デプロイ計画

### 11.1 デプロイ先
**推奨**: Railway
- 無料枠: 月500時間
- PostgreSQLアドオン利用可能
- GitHub連携で自動デプロイ

### 11.2 デプロイ前チェックリスト
- [ ] requirements.txt更新
- [ ] 環境変数設定
- [ ] PostgreSQL接続設定
- [ ] マイグレーション実行
- [ ] 動作確認

---

## 12. トラブルシューティング

### 12.1 よくある問題

#### Reflexが起動しない
```bash
# キャッシュクリア
reflex clean
rm -rf .web
reflex run
```

#### データベース接続エラー
- DATABASE_URLの確認
- マイグレーション実行確認

#### Threads API エラー
- アクセストークンの有効期限確認
- レート制限の確認
- エンドポイントURLの確認

### 12.2 デバッグ方法
- Reflexのログ確認: コンソール出力
- データベース確認: SQLiteブラウザ使用
- API呼び出し確認: ログ出力、Postman使用

---

## 13. 連絡先・リソース

### 13.1 公式ドキュメント
- [Threads API](https://developers.facebook.com/docs/threads)
- [Reflex](https://reflex.dev/docs/getting-started/introduction/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [APScheduler](https://apscheduler.readthedocs.io/)

### 13.2 参考リソース
- Reflex Examples: https://github.com/reflex-dev/reflex-examples
- Threads API Community: Meta Developers Forum

---

## 14. 次のステップ

### 14.1 実装済み確認
- [x] Phase 0: プロジェクトセットアップ完了
- [x] Phase 1: データベース設計・実装完了
- [x] Phase 2: ユーティリティ・共通機能完了
- [x] Phase 3: サービス層実装完了（7サービス）
- [x] Phase 4: スケジューラー実装完了
- [x] Phase 5: UI実装完了（基本部分）
- [x] 動作確認テスト実行済み（test_setup.py, test_services.py, test_scheduler.py）
- [x] Reflexアプリ起動確認済み
- [x] Gitリポジトリ初期化完了

### 14.2 次のタスク
**Phase 5 追加実装**または**Phase 6: エラーハンドリング・ロギング**から選択してください。

**Phase 5 追加実装**（推奨）:
- スケジュール設定ページの詳細実装
- 手動投稿ページの実装
- メトリクス分析ページの実装

**Phase 6: エラーハンドリング・ロギング**:
- グローバルエラーハンドラー
- UI側のエラー表示
- ロギング設定

[implementation_checklist.md](./implementation_checklist.md)を参照。

---

## 15. 質問・不明点がある場合

### 15.1 確認すべきドキュメント
1. 本ドキュメント（handover.md）
2. requirements.md
3. implementation_checklist.md
4. Threads API公式ドキュメント

### 15.2 判断に迷った場合
- **要件**: requirements.mdに立ち返る
- **実装方法**: 公式ドキュメント参照
- **優先度**: implementation_checklist.mdの優先度マーク参照

---

## 16. 重要な設計判断の記録

### 16.1 なぜReflexを選んだか
- Python純正でフロントエンド・バックエンド統合
- サイドメニュー対応
- モダンなUI
- 学習コスト低

### 16.2 なぜSQLite → PostgreSQL移行か
- 初期開発の容易さ（SQLite）
- 本番環境のスケーラビリティ（PostgreSQL）
- SQLAlchemyで移行容易

### 16.3 なぜログイン機能を後回しにしたか
- MVP優先
- 初期はローカル/単一ユーザー想定
- 将来的な拡張を考慮した設計

---

## 17. 成功の定義

### 17.1 MVP完成の基準
- [ ] 100アカウント登録可能
- [ ] 投稿グループ作成・管理可能
- [ ] 手動投稿（単一・一括）実行可能
- [ ] スケジュール設定・自動投稿実行可能
- [ ] 基本的なメトリクス表示可能

### 17.2 本番リリースの基準
- [ ] 全機能実装完了
- [ ] テスト完了
- [ ] Railwayにデプロイ完了
- [ ] 24時間安定稼働確認

---

**引き継ぎ日**: 2025年1月
**ドキュメントバージョン**: 1.1
**最終更新**: 2025年1月（Phase 0-5 完了時）

---

## 19. プロジェクト構成の重要な注意点

### 19.1 スクリプトの配置
- **開発・テスト用スクリプト**: `scripts/`ディレクトリに配置
- **プロジェクトルート**: アプリケーション本体と設定ファイルのみ
- **実行方法**: プロジェクトルートから`python scripts/<script_name>.py`で実行

### 19.2 Reflexの注意点
- **Setter定義**: Reflex 0.8.9以降は明示的にsetterメソッドを定義
- **条件分岐**: Pythonの`if`ではなく`rx.cond`を使用
- **パス設定**: scriptsディレクトリのスクリプトには`sys.path.insert(0, ...)`が必要
**Gitリポジトリ**: https://github.com/kokiada/threads-app.git

---

## 18. 実装済み機能の確認方法

### 18.1 動作確認テスト

#### サービス層テスト
```bash
# 仮想環境をアクティベート
source venv/bin/activate  # Windows: venv\Scripts\activate

# テスト実行
python scripts/test_setup.py
python scripts/test_services.py
```

#### Reflexアプリ起動
```bash
reflex run
```

ブラウザで http://localhost:3000 にアクセスして動作確認。

詳細は [how_to_run.md](./how_to_run.md) を参照。た
✓ すべてのテストが成功しました！
```

### 18.2 データベース初期化
```bash
python init_db.py
```

### 18.3 実装済みファイル一覧
```
threads/
├── models/              ✅ 7モデル実装済み
│   ├── base.py         (DB接続設定)
│   ├── account.py      (アカウント)
│   ├── post_group.py   (投稿グループ)
│   ├── post.py         (投稿)
│   ├── account_group.py (中間テーブル)
│   ├── schedule.py     (スケジュール)
│   ├── post_history.py (投稿履歴)
│   └── metrics_cache.py (メトリクスキャッシュ)
├── utils/               ✅ ユーティリティ実装済み
│   ├── crypto.py       (暗号化/復号化)
│   ├── validators.py   (バリデーション)
│   └── exceptions.py   (カスタム例外)
├── api/                 ✅ APIクライアント実装済み
│   └── threads_client.py (Threads API連携)
├── services/            ⏳ Phase 3で実装予定
├── scheduler/           ⏳ Phase 4で実装予定
├── pages/               ⏳ Phase 5で実装予定
└── components/          ⏳ Phase 5で実装予定
```

---

## 📌 最後に

このプロジェクトは**Phase 0-2が完了**し、基盤が整備されています。

**完了済み**:
- ✅ プロジェクトセットアップ
- ✅ データベース設計（全7モデル）
- ✅ ユーティリティ（暗号化、バリデーション、例外処理）
- ✅ Threads APIクライアント
- ✅ 動作確認テスト

**次のステップ**:
- Phase 3: サービス層実装（AccountService, PostService等）
- Phase 4: スケジューラー実装
- Phase 5: Reflex UI実装

**implementation_checklist.md**に沿って、Phase 3から実装を進めてください。

不明点があれば、まずドキュメントを確認し、それでも解決しない場合は公式ドキュメントを参照してください。

**Good luck with the implementation! 🚀**
