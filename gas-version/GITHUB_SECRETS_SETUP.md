# 🔑 GitHub Secrets セットアップガイド

現在の環境変数に合わせたGitHub Secrets設定方法です。

## 📋 必要なGitHub Secrets

以下の6つのSecretsをGitHubリポジトリに設定してください：

### 1. **ACCESS_TOKEN**
```
名前: ACCESS_TOKEN
値: ya29.a0AfH6SMB... (Google OAuth アクセストークン)
```

### 2. **REFRESH_TOKEN**  
```
名前: REFRESH_TOKEN
値: 1//04... (Google OAuth リフレッシュトークン)
```

### 3. **ID_TOKEN**
```
名前: ID_TOKEN  
値: eyJhbGciOiJSUzI1NiIsImtpZCI6... (Google OAuth IDトークン)
```

### 4. **CLIENTID**
```
名前: CLIENTID
値: 1234567890-abc...apps.googleusercontent.com (Google OAuth クライアントID)
```

### 5. **CLIENTSECRET**
```
名前: CLIENTSECRET
値: GOCSPX-... (Google OAuth クライアントシークレット)
```

### 6. **GAS_SCRIPT_ID**
```
名前: GAS_SCRIPT_ID
値: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms (GASプロジェクトのスクリプトID)
```

## 🔧 GitHub Secrets設定手順

### 1. GitHubリポジトリページにアクセス

### 2. Settings → Secrets and variables → Actions

### 3. 「New repository secret」をクリックして上記6つを追加

## 🚀 動作確認

設定完了後、以下で動作確認：

```bash
# gas-versionディレクトリで何かファイルを編集
git add gas-version/
git commit -m "Test auto deploy"
git push origin main
```

## 📊 ワークフロー概要

**トリガー条件**:
- mainブランチへのpush
- gas-version/内のファイル変更時のみ

**実行内容**:
1. 認証情報でclasp設定
2. コードをGASにプッシュ
3. ウェブアプリとしてデプロイ
4. デプロイ情報を表示

## 🔍 トラブルシューティング

### よくあるエラー

#### 1. 認証エラー
```
Error: Invalid credentials
```
**解決**: 各トークンが正しく設定されているか確認

#### 2. スクリプトIDエラー
```
Error: Script not found  
```
**解決**: `GAS_SCRIPT_ID`が正しいか確認

#### 3. 権限エラー
```
Error: Permission denied
```
**解決**: Google Apps Script APIが有効化されているか確認

## ✅ 成功時の期待される動作

- Git pushで自動的にGASプロジェクトが更新される
- GitHub Actionsログに成功メッセージが表示される
- GASエディタで最新コードが確認できる
- 新しいデプロイバージョンが作成される