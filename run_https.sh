#!/bin/bash
# HTTPS対応でReflexアプリを起動

# SSL証明書が存在しない場合は生成
if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
    echo "SSL証明書を生成中..."
    bash scripts/generate_ssl_cert.sh
fi

echo "HTTPS対応でReflexアプリを起動します..."
echo "アクセス: https://localhost:3000"
echo ""
echo "⚠️ 注意: ブラウザで「安全でない」警告が表示されます"
echo "   → 「詳細設定」→「localhost にアクセスする（安全ではありません）」をクリック"
echo ""

# Reflexアプリを起動（HTTPS対応）
/home/koki/work/threads/venv/bin/reflex run --backend-only &
BACKEND_PID=$!

# フロントエンドをHTTPSで起動
cd .web
HTTPS=true SSL_CRT_FILE=../ssl/cert.pem SSL_KEY_FILE=../ssl/key.pem npm run dev -- --port 3000

# 終了時にバックエンドも停止
kill $BACKEND_PID
