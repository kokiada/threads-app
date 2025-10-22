FROM python:3.12-slim

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ
WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコピー
COPY . .

# Reflexの初期化
RUN reflex init

# ポート公開
EXPOSE 8000

# 起動コマンド
CMD ["reflex", "run", "--env", "prod"]
