# Threads投稿マネージャー - Google Apps Script版

CLIからGASプロジェクトを管理できるclasp対応版です。

## 🚀 クイックスタート

### 1. clasp認証

```bash
npm run login
```

### 2. 新しいGASプロジェクト作成

```bash
npm run create
```

### 3. コードをアップロード

```bash
npm run push
```

### 4. ウェブアプリとしてデプロイ

```bash
npm run deploy
```

## 📋 利用可能なコマンド

### 基本操作
```bash
npm run login          # Google アカウントでログイン
npm run logout         # ログアウト
npm run create         # 新しいGASプロジェクトを作成
npm run clone          # 既存のGASプロジェクトをクローン
```

### 開発
```bash
npm run push           # ローカルコードをGASにアップロード
npm run pull           # GASからローカルにダウンロード
npm run dev            # ファイル変更を監視して自動アップロード
npm run open           # GASエディタをブラウザで開く
```

### デプロイ・管理
```bash
npm run deploy         # ウェブアプリとしてデプロイ
npm run prod           # プッシュ&デプロイを一括実行
npm run versions       # デプロイ履歴を表示
npm run logs           # 実行ログを表示
npm run status         # プロジェクト状態を確認
```

### ワンクリックセットアップ
```bash
npm run setup          # ログイン→プロジェクト作成→プッシュを一括実行
```

## 📁 ファイル構造

```
gas-version/
├── .clasp.json              # clasp設定ファイル
├── appsscript.json          # GASプロジェクト設定
├── package.json             # npm設定
├── src/                     # ソースコード（GASにアップロードされる）
│   ├── Code.js             # メインロジック
│   ├── dashboard.html      # ダッシュボードUI
│   ├── setup-test.js       # テスト用セットアップ
│   └── appsscript.json     # GAS設定（コピー）
├── Code.gs                  # 元ファイル（参考用）
├── dashboard.html           # 元ファイル（参考用）
└── setup-test.gs           # 元ファイル（参考用）
```

## 🔧 初回セットアップ手順

### 1. Google Apps Script API有効化

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成または既存のプロジェクトを選択
3. 「APIs & Services」→「Library」
4. 「Google Apps Script API」を検索して有効化

### 2. 認証とプロジェクト作成

```bash
# Google アカウントで認証
npm run login

# 新しいGASプロジェクトを作成
npm run create

# 生成されたスクリプトIDを確認
cat .clasp.json
```

### 3. コードをアップロード

```bash
# ローカルコードをGASにアップロード
npm run push

# GASエディタで確認
npm run open
```

### 4. ウェブアプリデプロイ

```bash
# ウェブアプリとしてデプロイ
npm run deploy

# デプロイURLを取得
npm run versions
```

## 🔄 既存プロジェクトとの連携

既存のGASプロジェクトがある場合：

```bash
# 既存プロジェクトのスクリプトIDを.clasp.jsonに設定
echo '{"scriptId":"YOUR_SCRIPT_ID","rootDir":"./src"}' > .clasp.json

# GASからローカルに同期
npm run pull

# ローカルからGASに同期
npm run push
```

## 🧪 テスト・デバッグ

```bash
# 実行ログを確認
npm run logs

# プロジェクト状態を確認
npm run status

# GASエディタを開いてテスト関数を実行
npm run open
```

## 🔑 環境変数設定

GASエディタで以下の環境変数を設定：

```
プロジェクトの設定 → スクリプトプロパティ:
- THREADS_CLIENT_ID: your_threads_client_id
- THREADS_CLIENT_SECRET: your_threads_client_secret
```

## 🚨 注意事項

- `.clasp.json`にはスクリプトIDが含まれるため、公開リポジトリでは注意が必要
- `src/`ディレクトリ内のファイルのみがGASにアップロードされます
- HTMLファイルは`.html`拡張子のまま、JSファイルは`.js`拡張子を使用
- `appsscript.json`はプロジェクト設定ファイルです

## 📖 clasp公式ドキュメント

- [clasp GitHub](https://github.com/google/clasp)
- [clasp公式ドキュメント](https://developers.google.com/apps-script/guides/clasp)