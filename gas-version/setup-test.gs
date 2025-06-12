/**
 * GAS版テスト用セットアップスクリプト
 * このファイルの内容をApps Scriptエディタにコピーして実行してください
 */

/**
 * 🚀 ワンクリックセットアップ関数
 * この関数を実行するだけで初期設定が完了します
 */
function quickSetup() {
  console.log('🚀 Threads投稿マネージャー セットアップ開始...');
  
  try {
    // 1. スプレッドシート作成
    console.log('📊 データ用スプレッドシートを作成中...');
    const spreadsheetId = setupSpreadsheet();
    
    // 2. トリガー設定
    console.log('⏰ 自動実行トリガーを設定中...');
    setupTriggers();
    
    // 3. テストデータ作成
    console.log('🧪 テストデータを作成中...');
    createTestData();
    
    // 4. 結果表示
    console.log('✅ セットアップ完了！');
    console.log('📁 スプレッドシートID:', spreadsheetId);
    console.log('🌐 次のステップ: ウェブアプリとしてデプロイしてください');
    console.log('');
    console.log('📋 チェックリスト:');
    console.log('  ✅ スプレッドシート作成完了');
    console.log('  ✅ トリガー設定完了');
    console.log('  ✅ テストデータ作成完了');
    console.log('  ⏳ ウェブアプリデプロイ（手動）');
    console.log('  ⏳ 環境変数設定（手動）');
    
    return {
      success: true,
      spreadsheetId: spreadsheetId,
      message: 'セットアップが正常に完了しました'
    };
    
  } catch (error) {
    console.error('❌ セットアップエラー:', error.toString());
    return {
      success: false,
      error: error.toString()
    };
  }
}

/**
 * 🧪 テストデータの作成
 */
function createTestData() {
  try {
    // テストアカウントを作成
    const testAccount = {
      name: 'テストアカウント',
      username: 'test_user',
      accessToken: 'test_token_' + Utilities.getUuid(),
      tokenExpiry: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString() // 60日後
    };
    
    addAccount(testAccount);
    console.log('📝 テストアカウントを作成しました:', testAccount.name);
    
    // テストスケジュール投稿を作成
    const testSchedule = {
      accountId: '1', // 最初のアカウントのIDを仮定
      accountName: testAccount.name,
      content: {
        mediaType: 'TEXT',
        text: 'これはテスト投稿です。GAS版の動作確認中です。 #ThreadsAPI #GoogleAppsScript',
        replyControl: 'everyone'
      },
      scheduledTime: new Date(Date.now() + 60 * 60 * 1000).toISOString() // 1時間後
    };
    
    schedulePost(testSchedule);
    console.log('📅 テストスケジュール投稿を作成しました');
    
  } catch (error) {
    console.warn('⚠️ テストデータ作成中にエラー:', error.toString());
  }
}

/**
 * 🔍 システム状態チェック
 */
function checkSystemStatus() {
  console.log('🔍 システム状態をチェック中...');
  
  try {
    // スプレッドシート接続チェック
    const spreadsheetId = PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID');
    if (spreadsheetId) {
      const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
      console.log('✅ スプレッドシート接続: 正常');
      console.log('📊 スプレッドシート名:', spreadsheet.getName());
    } else {
      console.log('❌ スプレッドシート接続: 未設定');
    }
    
    // トリガーチェック
    const triggers = ScriptApp.getProjectTriggers();
    console.log('⏰ トリガー数:', triggers.length);
    triggers.forEach((trigger, index) => {
      console.log(`  ${index + 1}. ${trigger.getHandlerFunction()} - ${trigger.getTriggerSource()}`);
    });
    
    // 環境変数チェック
    const clientId = PropertiesService.getScriptProperties().getProperty('THREADS_CLIENT_ID');
    const clientSecret = PropertiesService.getScriptProperties().getProperty('THREADS_CLIENT_SECRET');
    
    console.log('🔑 環境変数設定:');
    console.log('  THREADS_CLIENT_ID:', clientId ? '設定済み' : '未設定');
    console.log('  THREADS_CLIENT_SECRET:', clientSecret ? '設定済み' : '未設定');
    
    // データ件数チェック
    const accounts = getAccounts();
    const scheduledPosts = getScheduledPosts();
    const postHistory = getPostHistory();
    
    console.log('📊 データ統計:');
    console.log('  アカウント数:', accounts.length);
    console.log('  スケジュール投稿数:', scheduledPosts.length);
    console.log('  投稿履歴数:', postHistory.length);
    
    return {
      spreadsheet: !!spreadsheetId,
      triggers: triggers.length,
      environment: !!clientId && !!clientSecret,
      accounts: accounts.length,
      schedules: scheduledPosts.length,
      history: postHistory.length
    };
    
  } catch (error) {
    console.error('❌ システム状態チェックエラー:', error.toString());
    return { error: error.toString() };
  }
}

/**
 * 🧹 システムリセット（注意：全データが削除されます）
 */
function resetSystem() {
  const confirm = Browser.msgBox(
    'システムリセット',
    '本当にシステムをリセットしますか？\n\n⚠️ 全てのデータが削除されます：\n- スプレッドシートデータ\n- トリガー設定\n- 環境変数\n\nこの操作は取り消せません。',
    Browser.Buttons.YES_NO
  );
  
  if (confirm !== Browser.Buttons.YES) {
    console.log('ℹ️ リセット操作がキャンセルされました');
    return;
  }
  
  console.log('🧹 システムリセット開始...');
  
  try {
    // トリガー削除
    ScriptApp.getProjectTriggers().forEach(trigger => {
      ScriptApp.deleteTrigger(trigger);
    });
    console.log('⏰ トリガーを削除しました');
    
    // スプレッドシートデータクリア
    const spreadsheetId = PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID');
    if (spreadsheetId) {
      const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
      const sheets = spreadsheet.getSheets();
      sheets.forEach(sheet => {
        if (sheet.getDataRange().getNumRows() > 1) {
          sheet.getRange(2, 1, sheet.getLastRow() - 1, sheet.getLastColumn()).clear();
        }
      });
      console.log('📊 スプレッドシートデータをクリアしました');
    }
    
    // 環境変数削除（オプション）
    // PropertiesService.getScriptProperties().deleteProperty('THREADS_CLIENT_ID');
    // PropertiesService.getScriptProperties().deleteProperty('THREADS_CLIENT_SECRET');
    
    console.log('✅ システムリセット完了');
    
  } catch (error) {
    console.error('❌ リセットエラー:', error.toString());
  }
}

/**
 * 📖 ヘルプ情報表示
 */
function showHelp() {
  console.log('📖 Threads投稿マネージャー GAS版 ヘルプ');
  console.log('');
  console.log('🚀 主要な関数:');
  console.log('  quickSetup()       - ワンクリック初期セットアップ');
  console.log('  checkSystemStatus() - システム状態チェック');
  console.log('  resetSystem()      - システムリセット（注意）');
  console.log('  createTestData()   - テストデータ作成');
  console.log('');
  console.log('🔧 メンテナンス関数:');
  console.log('  setupSpreadsheet() - スプレッドシート再作成');
  console.log('  setupTriggers()    - トリガー再設定');
  console.log('  processScheduledPosts() - 手動スケジュール実行');
  console.log('');
  console.log('📊 データ操作関数:');
  console.log('  getAccounts()      - アカウント一覧取得');
  console.log('  getScheduledPosts() - スケジュール投稿一覧');
  console.log('  getPostHistory()   - 投稿履歴取得');
  console.log('');
  console.log('💡 使用方法:');
  console.log('  1. quickSetup() を実行');
  console.log('  2. ウェブアプリとしてデプロイ');
  console.log('  3. 環境変数（API キー）を設定');
  console.log('  4. デプロイURLでダッシュボードにアクセス');
}

/**
 * 🧪 API接続テスト（モック）
 */
function testAPIConnection() {
  console.log('🧪 API接続テスト開始...');
  
  try {
    // 環境変数チェック
    const clientId = PropertiesService.getScriptProperties().getProperty('THREADS_CLIENT_ID');
    const clientSecret = PropertiesService.getScriptProperties().getProperty('THREADS_CLIENT_SECRET');
    
    if (!clientId || !clientSecret) {
      throw new Error('Threads API認証情報が設定されていません');
    }
    
    console.log('✅ 環境変数設定: 正常');
    
    // テストアカウントで投稿テスト（実際のAPIコールなし）
    console.log('🔍 投稿処理テスト...');
    
    const testPostData = {
      accountId: 'test',
      mediaType: 'TEXT',
      text: 'API接続テスト投稿（実際には投稿されません）',
      replyControl: 'everyone'
    };
    
    // モック処理のみ実行
    console.log('📝 テスト投稿データ:', JSON.stringify(testPostData, null, 2));
    console.log('✅ API接続テスト完了（モック実行）');
    
    return {
      success: true,
      message: 'API接続テストが正常に完了しました（モック実行）'
    };
    
  } catch (error) {
    console.error('❌ API接続テストエラー:', error.toString());
    return {
      success: false,
      error: error.toString()
    };
  }
}