#!/bin/bash

# GitHub Secrets セットアップ支援スクリプト
# このスクリプトは認証情報の取得を支援します（自動設定はしません）

echo "🔑 GitHub Secrets セットアップ支援"
echo "=================================="
echo ""

# clasp認証状況チェック
echo "📋 1. CLASP認証情報の確認"
echo "------------------------"

if [ -f ~/.clasprc.json ]; then
    echo "✅ clasp認証情報が見つかりました"
    echo ""
    echo "🔍 認証情報（GitHub Secretsに設定してください）:"
    echo "名前: CLASP_CREDENTIALS"
    echo "値:"
    echo "----------------------------------------"
    cat ~/.clasprc.json
    echo "----------------------------------------"
    echo ""
else
    echo "❌ clasp認証情報が見つかりません"
    echo "以下のコマンドで認証してください:"
    echo "  npm run login"
    echo ""
fi

# スクリプトIDチェック
echo "📋 2. GASスクリプトIDの確認"
echo "-------------------------"

if [ -f .clasp.json ]; then
    SCRIPT_ID=$(cat .clasp.json | grep -o '"scriptId":"[^"]*"' | cut -d'"' -f4)
    if [ ! -z "$SCRIPT_ID" ]; then
        echo "✅ 現在のスクリプトID: $SCRIPT_ID"
        echo ""
        echo "🔍 GitHub Secretsに設定してください:"
        echo "本番環境用："
        echo "  名前: GAS_SCRIPT_ID_PROD"
        echo "  値: $SCRIPT_ID"
        echo ""
        echo "開発環境用："
        echo "  名前: GAS_SCRIPT_ID_DEV"  
        echo "  値: $SCRIPT_ID（または別のプロジェクトID）"
        echo ""
    else
        echo "❌ スクリプトIDが設定されていません"
    fi
else
    echo "❌ .clasp.jsonが見つかりません"
    echo "以下のコマンドでGASプロジェクトを作成してください:"
    echo "  npm run create"
    echo ""
fi

# GitHub Secrets設定手順
echo "📋 3. GitHub Secrets設定手順"
echo "---------------------------"
echo "1. GitHubリポジトリページにアクセス"
echo "2. Settings → Secrets and variables → Actions"
echo "3. 'New repository secret' をクリック"
echo "4. 以下のSecretsを追加:"
echo ""
echo "   CLASP_CREDENTIALS:"
echo "   └── 上記の認証情報をJSONとして貼り付け"
echo ""
echo "   GAS_SCRIPT_ID_PROD:"
echo "   └── 本番用GASプロジェクトのスクリプトID"
echo ""
echo "   GAS_SCRIPT_ID_DEV:"
echo "   └── 開発用GASプロジェクトのスクリプトID"
echo ""

# 動作確認コマンド
echo "📋 4. 動作確認"
echo "-------------"
echo "GitHub Secrets設定後、以下で動作確認できます:"
echo ""
echo "  # gas-versionディレクトリで何かファイルを編集"
echo "  git add gas-version/"
echo "  git commit -m 'Test GAS auto deploy'"
echo "  git push origin develop  # 開発環境テスト"
echo "  git push origin main     # 本番環境テスト"
echo ""

echo "✅ セットアップ情報の確認が完了しました"
echo "詳細は GITHUB_ACTIONS_SETUP.md を参照してください"