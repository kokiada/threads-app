# 🚀 claspセットアップ完了！

CLIからGASプロジェクトを管理できるようになりました。

## ✅ 完了した作業

- ✅ clasp グローバルインストール
- ✅ プロジェクト設定ファイル作成
- ✅ ファイル構造整理（src/ディレクトリ）
- ✅ npm スクリプト設定
- ✅ ドキュメント作成

## 🎯 次の手順

### 1. **Google Apps Script API 有効化**

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを選択（または新規作成）
3. 「APIs & Services」→「Library」
4. 「Google Apps Script API」を検索→有効化

### 2. **clasp認証**

```bash
cd gas-version
npm run login
```

### 3. **新規GASプロジェクト作成**

```bash
npm run create
```

または既存プロジェクトを使用する場合：

```bash
# .clasp.jsonにスクリプトIDを設定
echo '{"scriptId":"YOUR_SCRIPT_ID","rootDir":"./src"}' > .clasp.json
```

### 4. **コードをプッシュ**

```bash
npm run push
```

### 5. **ウェブアプリデプロイ**

```bash
npm run deploy
```

## 🔧 便利なコマンド

```bash
# 開発時（ファイル監視で自動プッシュ）
npm run dev

# GASエディタを開く
npm run open

# ログ確認
npm run logs

# 状態確認
npm run status

# プッシュ＆デプロイ
npm run prod
```

## 📁 ファイル構造

```
gas-version/
├── src/                    # ← GASにアップロードされるファイル
│   ├── Code.js            # メインロジック
│   ├── dashboard.html     # UI
│   ├── setup-test.js      # テスト用
│   └── appsscript.json    # GAS設定
├── .clasp.json            # clasp設定
├── package.json           # npm設定
└── README.md              # 詳細ガイド
```

## 🚨 重要な注意点

1. **API有効化**: 最初にGoogle Apps Script APIを有効化してください
2. **認証**: `npm run login`で必ずGoogleアカウント認証を行ってください
3. **スクリプトID**: `.clasp.json`の`scriptId`は作成後に自動設定されます
4. **src/ディレクトリ**: このディレクトリ内のファイルのみがGASにアップロードされます

claspのセットアップが完了しました！`npm run login`から始めてください。