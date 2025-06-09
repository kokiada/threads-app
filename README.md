# Threads投稿マネージャー

Threadsへの投稿を自動化するモダンなダッシュボードアプリケーション

## 概要

Threads投稿マネージャーは、複数のThreadsアカウントを管理し、投稿のスケジューリングを可能にするWebアプリケーションです。Next.js 15とReact 19を使用して構築され、モバイルファーストのレスポンシブデザインを特徴としています。

## 主な機能

### 実装済み機能
- 📱 **レスポンシブダッシュボード** - モバイル・デスクトップ両対応
- 👥 **アカウント管理** - 複数アカウントの表示・管理UI
- 📝 **投稿作成UI** - モーダルベースの投稿作成インターフェース
- 📅 **スケジュール設定** - 即座投稿・スケジュール投稿選択
- 📊 **ダッシュボード** - アカウント概要、投稿履歴、統計表示
- 🎨 **モダンUI** - shadcn/ui + Tailwind CSSによる美しいインターフェース

### 開発予定機能
- 🔌 **Threads API連携** - 実際の投稿機能
- 🚀 **自動投稿** - スケジュール実行機能
- 📸 **メディアアップロード** - 画像・動画対応
- 📈 **分析機能** - 投稿パフォーマンス追跡
- 🔔 **通知システム** - 投稿結果通知

## 技術スタック

- **フレームワーク**: Next.js 15
- **言語**: TypeScript
- **UI**: React 19 + shadcn/ui + Tailwind CSS
- **アイコン**: Lucide React
- **スタイリング**: Tailwind CSS
- **デプロイ**: Vercel対応

## 開発環境

### 必要な環境
- Node.js 18.17以上
- npm または yarn

### セットアップ

1. リポジトリをクローン
```bash
git clone <repository-url>
cd threads-app
```

2. 依存関係をインストール
```bash
npm install
```

3. 開発サーバーを起動
```bash
npm run dev
```

4. ブラウザで http://localhost:3000 を開く

### 開発コマンド

```bash
# 開発サーバー起動（Turbo付き）
npm run dev

# プロダクションビルド
npm run build

# プロダクションサーバー起動
npm start

# ESLintでコード品質チェック
npm run lint
```

## プロジェクト構造

```
threads-app/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # ルートレイアウト
│   ├── page.tsx           # メインページ
│   └── globals.css        # グローバルスタイル
├── components/
│   └── ui/                # shadcn/ui コンポーネント
├── lib/
│   └── utils.ts           # ユーティリティ関数
├── threads-manager.tsx    # メインダッシュボードコンポーネント
└── public/                # 静的ファイル
```

## 現在の実装状況

このプロジェクトは現在**フロントエンドUIの実装段階**です：

- ✅ ダッシュボード画面
- ✅ アカウント管理画面
- ✅ 投稿作成モーダル
- ✅ レスポンシブデザイン
- ✅ モックデータによる動作確認
- 🚧 バックエンドAPI連携
- 🚧 実際のThreads投稿機能
- 🚧 データ永続化

## 貢献

このプロジェクトへの貢献を歓迎します。Issue報告やPull Requestをお待ちしています。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 詳細ドキュメント

- [要件定義書](./Docs/threads-app-requirements-md.md)
- [開発ガイド](./CLAUDE.md)