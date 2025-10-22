# HTTPS対応セットアップガイド

## 概要

Threads APIはHTTPSが必須です。開発環境でHTTPSを使用する方法を説明します。

## 方法1: 簡単な起動（推奨）

```bash
chmod +x run_https.sh
./run_https.sh
```

これで自動的にSSL証明書が生成され、HTTPSでアプリが起動します。

## 方法2: 手動セットアップ

### ステップ1: SSL証明書の生成

```bash
bash scripts/generate_ssl_cert.sh
```

### ステップ2: Reflexアプリの起動

```bash
# バックエンドを起動
/home/koki/work/threads/venv/bin/reflex run --backend-only &

# フロントエンドをHTTPSで起動
cd .web
HTTPS=true SSL_CRT_FILE=../ssl/cert.pem SSL_KEY_FILE=../ssl/key.pem npm run dev -- --port 3000
```

## アクセス方法

1. ブラウザで `https://localhost:3000` にアクセス
2. 「安全でない」警告が表示される
3. 「詳細設定」をクリック
4. 「localhost にアクセスする（安全ではありません）」をクリック

## Threads API認証の流れ

1. `https://localhost:3000/auth` にアクセス
2. 「Threadsで認証する」ボタンをクリック
3. Threadsで認証
4. リダイレクト後のURLから認証コードをコピー
5. 認証コードを入力してアクセストークンを取得

## トラブルシューティング

### SSL証明書エラー

**問題**: ブラウザが証明書を信頼しない

**解決方法**:
- 開発用の自己署名証明書なので、警告を無視して進む
- または、証明書をシステムの信頼ストアに追加

### ポートが使用中

**問題**: `Error: listen EADDRINUSE: address already in use :::3000`

**解決方法**:
```bash
# 既存のプロセスを停止
pkill -f "reflex run"
pkill -f "npm run dev"
```

### Meta Developer設定

Threads APIアプリの設定で、リダイレクトURIを以下に設定してください:

```
https://localhost:3000/auth/callback
```

## 本番環境

本番環境では、適切なSSL証明書（Let's Encryptなど）を使用してください。

Railwayなどのホスティングサービスは自動的にHTTPSを提供します。
