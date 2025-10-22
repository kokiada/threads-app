#!/bin/bash
# SSL証明書生成スクリプト（開発用）

mkdir -p ssl

openssl req -x509 -newkey rsa:4096 -nodes \
  -out ssl/cert.pem \
  -keyout ssl/key.pem \
  -days 365 \
  -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Development/CN=localhost"

echo "✅ SSL証明書を生成しました"
echo "   証明書: ssl/cert.pem"
echo "   秘密鍵: ssl/key.pem"
