# 🚀 GitHub Actions自動デプロイセットアップ

Git pushでGASへ自動デプロイする設定手順です。

## 📋 必要なGitHub Secrets

以下の認証情報をGitHubリポジトリのSecretsに設定してください。

### 1. **CLASP_CREDENTIALS**

clasp認証情報（`.clasprc.json`の内容）

#### 取得手順:
```bash
# ローカルでclasp認証
cd gas-version
npm run login

# 認証情報を確認
cat ~/.clasprc.json
```

内容例:
```json
{
  "token": {
    "access_token": "ya29.a0AfH6SMB...",
    "refresh_token": "1//04...",
    "scope": "https://www.googleapis.com/auth/script.projects https://www.googleapis.com/auth/drive.file",
    "token_type": "Bearer",
    "expiry_date": 1234567890123
  },
  "oauth2ClientSettings": {
    "clientId": "1234567890-abc...apps.googleusercontent.com",
    "clientSecret": "GOCSPX-...",
    "redirectUri": "http://localhost"
  },
  "isLocalCreds": false
}
```

### 2. **GAS_SCRIPT_ID_PROD** (本番環境)

本番用GASプロジェクトのスクリプトID

#### 取得手順:
```bash
# 本番用GASプロジェクト作成
npm run create

# スクリプトIDを確認
cat .clasp.json
```

### 3. **GAS_SCRIPT_ID_DEV** (開発環境)

開発用GASプロジェクトのスクリプトID

#### 取得手順:
```bash
# 開発用に別のGASプロジェクトを作成
# または既存プロジェクトのIDを使用
```

## 🔧 GitHub Secrets設定手順

### 1. GitHubリポジトリページにアクセス

### 2. Settings → Secrets and variables → Actions

### 3. 「New repository secret」をクリックして以下を追加:

```
Name: CLASP_CREDENTIALS
Value: {上記のclasp認証情報をJSONとして貼り付け}

Name: GAS_SCRIPT_ID_PROD  
Value: 本番用GASプロジェクトのスクリプトID

Name: GAS_SCRIPT_ID_DEV
Value: 開発用GASプロジェクトのスクリプトID
```

## 🚀 動作フロー

### 自動デプロイ条件

1. **main ブランチ**へのpush
   - 本番用GASプロジェクトにデプロイ
   - `GAS_SCRIPT_ID_PROD`を使用

2. **develop ブランチ**へのpush  
   - 開発用GASプロジェクトにデプロイ
   - `GAS_SCRIPT_ID_DEV`を使用

3. **gas-versionディレクトリ**内のファイル変更時のみ実行

### ワークフロー内容

1. ✅ **テスト実行**
   - JavaScript構文チェック
   - HTML構文チェック
   - appsscript.json検証

2. 🚀 **自動デプロイ**
   - clasp認証
   - コードプッシュ (`clasp push`)
   - ウェブアプリデプロイ (`clasp deploy`)

## 📊 使用例

### 1. 開発環境デプロイ

```bash
git checkout develop
# gas-version/内のファイルを編集
git add gas-version/
git commit -m "Update GAS dashboard UI"
git push origin develop
# → 自動的に開発用GASにデプロイ
```

### 2. 本番環境デプロイ

```bash
git checkout main
git merge develop
git push origin main
# → 自動的に本番用GASにデプロイ
```

## 🔍 デプロイ状況確認

### GitHub Actionsページで確認

1. リポジトリの「Actions」タブ
2. 「GAS Auto Deploy」ワークフローを選択
3. 実行ログでデプロイ状況を確認

### 成功時のログ例

```
✅ GAS deployment successful for refs/heads/main
🚀 GAS Deployment successful!
📋 Recent deployments:
- AKfycbz... (Latest) - Production deployment from commit abc123
```

## 🛠️ トラブルシューティング

### よくある問題

#### 1. 認証エラー
```
Error: Invalid credentials
```
**解決**: `CLASP_CREDENTIALS`を再設定

#### 2. スクリプトIDエラー  
```
Error: Script not found
```
**解決**: `GAS_SCRIPT_ID_PROD/DEV`を確認

#### 3. 権限エラー
```
Error: Permission denied
```
**解決**: Google Apps Script APIを有効化

### デバッグ手順

1. **ローカルで動作確認**
   ```bash
   cd gas-version
   npm run push
   npm run deploy
   ```

2. **GitHub Actionsログ確認**
   - 詳細なエラーメッセージを確認
   - 各ステップの実行結果を確認

3. **認証情報再取得**
   ```bash
   clasp logout
   clasp login
   cat ~/.clasprc.json
   ```

## 🎯 期待される結果

### ✅ 成功時の状態

- Git pushで自動的にGASが更新される
- 本番・開発環境が適切に分離される
- デプロイ履歴が残る
- エラー時に通知される

### 📈 効果

- **開発効率向上**: 手動デプロイ不要
- **環境分離**: 本番・開発の明確な分離
- **CI/CD実現**: 継続的インテグレーション
- **履歴管理**: デプロイ履歴の自動記録

## 🔗 関連ドキュメント

- [clasp公式ドキュメント](https://developers.google.com/apps-script/guides/clasp)
- [GitHub Actions公式ドキュメント](https://docs.github.com/en/actions)
- [Google Apps Script API](https://developers.google.com/apps-script/api)