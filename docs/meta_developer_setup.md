# Meta Developer セットアップガイド

## エラー: "The user has not accepted the invite to test the app"

このエラーは、Threadsアカウントがアプリのテスターとして登録されていないことを示しています。

## 解決方法

### ステップ1: Meta Developer Console にアクセス

1. https://developers.facebook.com/ にアクセス
2. 「マイアプリ」をクリック
3. Threads APIアプリを選択

### ステップ2: テスターを追加

1. 左メニューから「ロール」→「ロール」を選択
2. 「テスター」セクションまでスクロール
3. 「テスターを追加」ボタンをクリック
4. 使用するThreadsアカウントのユーザー名またはユーザーIDを入力
5. 「送信」をクリック

### ステップ3: 招待を承認

#### 方法A: Facebookで承認（推奨）

1. https://www.facebook.com/ にアクセス
2. 通知を確認
3. アプリのテスター招待を承認

#### 方法B: 直接リンクで承認

1. 以下のURLにアクセス:
   ```
   https://www.facebook.com/games/testing/
   ```
2. 保留中の招待を確認
3. 「承認」をクリック

### ステップ4: アプリモードを確認

1. Meta Developer Console で「設定」→「ベーシック」を選択
2. 「アプリモード」を確認
   - **開発モード**: テスターのみ使用可能（現在の状態）
   - **本番モード**: 全ユーザーが使用可能（審査が必要）

開発中は「開発モード」で問題ありません。

### ステップ5: リダイレクトURIの設定

1. 「設定」→「ベーシック」を選択
2. 「+ プラットフォームを追加」をクリック
3. 「ウェブサイト」を選択
4. 「サイトURL」に以下を入力:
   ```
   https://localhost:3000
   ```
5. 「変更を保存」をクリック

6. Threads API設定で「リダイレクトURI」を追加:
   ```
   https://localhost:3000/auth/callback
   ```

### ステップ6: 必要な権限を確認

Threads API設定で以下の権限が有効になっているか確認:

- ✅ threads_basic
- ✅ threads_content_publish
- ✅ threads_manage_insights
- ✅ threads_manage_replies
- ✅ threads_read_replies

## 再度認証を試す

1. Reflexアプリを起動: `./run_https.sh`
2. `https://localhost:3000/auth` にアクセス
3. 「Threadsで認証する」をクリック
4. 認証を完了

## トラブルシューティング

### テスター招待が表示されない

**原因**: FacebookアカウントとThreadsアカウントが紐付いていない

**解決方法**:
1. Threadsアプリを開く
2. 設定 → アカウント → Facebookとリンク

### 別のエラーが表示される

**エラー**: `redirect_uri_mismatch`

**解決方法**:
- Meta Developer Console のリダイレクトURIが `https://localhost:3000/auth/callback` と完全一致しているか確認

**エラー**: `Invalid OAuth access token`

**解決方法**:
- App ID と App Secret が正しいか `.env` ファイルを確認

## 本番環境への移行

開発が完了したら、以下の手順で本番モードに移行:

1. Meta Developer Console で「アプリレビュー」を選択
2. 必要な権限のレビューをリクエスト
3. 審査に合格後、「本番モード」に切り替え

本番モードでは、テスター登録なしで全ユーザーが使用できます。

## 参考リンク

- Meta Developer Console: https://developers.facebook.com/
- Threads API ドキュメント: https://developers.facebook.com/docs/threads
- アプリロール管理: https://developers.facebook.com/docs/development/build-and-test/app-roles

---

**重要**: 開発中は必ずテスターとして登録されたアカウントを使用してください。
