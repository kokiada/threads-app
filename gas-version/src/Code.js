/**
 * Threads 投稿マネージャー - Google Apps Script版
 * メイン処理ファイル
 */

// グローバル設定
const CONFIG = {
  SPREADSHEET_ID: PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID'),
  THREADS_CLIENT_ID: PropertiesService.getScriptProperties().getProperty('THREADS_CLIENT_ID'),
  THREADS_CLIENT_SECRET: PropertiesService.getScriptProperties().getProperty('THREADS_CLIENT_SECRET'),
  BASE_URL: ScriptApp.getService().getUrl()
};

/**
 * ウェブアプリのメインエントリーポイント
 */
function doGet(e) {
  const page = e.parameter.page || 'dashboard';
  
  switch (page) {
    case 'dashboard':
      return HtmlService.createTemplateFromFile('dashboard')
        .evaluate()
        .setTitle('Threads 投稿マネージャー')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
    
    case 'auth':
      return handleThreadsAuth(e);
    
    default:
      return HtmlService.createHtmlOutput('<h1>ページが見つかりません</h1>');
  }
}

/**
 * Threads OAuth認証処理
 */
function handleThreadsAuth(e) {
  const code = e.parameter.code;
  const state = e.parameter.state;
  const error = e.parameter.error;
  
  if (error) {
    return HtmlService.createHtmlOutput(`
      <h1>認証エラー</h1>
      <p>エラー: ${error}</p>
      <p>説明: ${e.parameter.error_description || ''}</p>
      <button onclick="window.close()">閉じる</button>
    `);
  }
  
  if (!code) {
    return HtmlService.createHtmlOutput(`
      <h1>認証失敗</h1>
      <p>認証コードが取得できませんでした。</p>
      <button onclick="window.close()">閉じる</button>
    `);
  }
  
  try {
    // アクセストークンを取得
    const tokenData = exchangeCodeForToken(code);
    
    // ユーザー情報を取得
    const userInfo = getThreadsUserInfo(tokenData.access_token);
    
    // アカウント情報を作成
    const accountData = {
      name: userInfo.name || userInfo.username,
      username: userInfo.username,
      accessToken: tokenData.access_token,
      refreshToken: tokenData.refresh_token || '',
      tokenExpiry: new Date(Date.now() + (tokenData.expires_in || 3600) * 1000).toISOString(),
      avatar: ''
    };
    
    // アカウントを追加
    const result = addAccount(accountData);
    
    return HtmlService.createHtmlOutput(`
      <h1>認証成功</h1>
      <p>アカウント「${accountData.name}」が追加されました！</p>
      <script>
        window.opener.postMessage({type: 'oauth_success', account: ${JSON.stringify(result)}}, '*');
        window.close();
      </script>
    `);
    
  } catch (error) {
    Logger.log('OAuth認証エラー: ' + error.toString());
    return HtmlService.createHtmlOutput(`
      <h1>認証処理エラー</h1>
      <p>エラー: ${error.message}</p>
      <button onclick="window.close()">閉じる</button>
    `);
  }
}

/**
 * 認証コードをアクセストークンに交換
 */
function exchangeCodeForToken(code) {
  const redirectUri = CONFIG.BASE_URL + '?page=auth';
  
  const response = UrlFetchApp.fetch('https://graph.threads.net/oauth/access_token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    payload: {
      'client_id': CONFIG.THREADS_CLIENT_ID,
      'client_secret': CONFIG.THREADS_CLIENT_SECRET,
      'grant_type': 'authorization_code',
      'redirect_uri': redirectUri,
      'code': code
    }
  });
  
  const responseData = JSON.parse(response.getContentText());
  
  if (response.getResponseCode() !== 200) {
    throw new Error('トークン取得失敗: ' + responseData.error_description);
  }
  
  return responseData;
}

/**
 * Threadsユーザー情報を取得
 */
function getThreadsUserInfo(accessToken) {
  const response = UrlFetchApp.fetch(
    `https://graph.threads.net/v1.0/me?fields=id,username,name&access_token=${accessToken}`
  );
  
  const userData = JSON.parse(response.getContentText());
  
  if (response.getResponseCode() !== 200) {
    throw new Error('ユーザー情報取得失敗: ' + userData.error.message);
  }
  
  return userData;
}

/**
 * OAuth認証URLを生成
 */
function generateOAuthUrl() {
  const redirectUri = CONFIG.BASE_URL + '?page=auth';
  
  const scope = 'threads_basic,threads_content_publish';
  const state = Utilities.getUuid();
  
  const authUrl = 'https://threads.net/oauth/authorize?' +
    'client_id=' + encodeURIComponent(CONFIG.THREADS_CLIENT_ID) +
    '&redirect_uri=' + encodeURIComponent(redirectUri) +
    '&scope=' + encodeURIComponent(scope) +
    '&response_type=code' +
    '&state=' + encodeURIComponent(state);
  
  return authUrl;
}

/**
 * POST リクエストの処理
 */
function doPost(e) {
  Logger.log('doPost called with parameters: ' + JSON.stringify(e.parameter));
  
  const action = e.parameter.action;
  
  try {
    // 初期設定が完了していない場合は自動で設定
    if (!CONFIG.SPREADSHEET_ID || CONFIG.SPREADSHEET_ID === '') {
      const spreadsheetId = setupSpreadsheet();
      CONFIG.SPREADSHEET_ID = spreadsheetId;
    }
    
    switch (action) {
      case 'getAccounts':
        const accounts = getAccounts();
        Logger.log('getAccounts result: ' + JSON.stringify(accounts));
        return ContentService
          .createTextOutput(JSON.stringify(accounts))
          .setMimeType(ContentService.MimeType.JSON);
      
      case 'addAccount':
        const accountData = JSON.parse(e.parameter.data);
        return ContentService
          .createTextOutput(JSON.stringify(addAccount(accountData)))
          .setMimeType(ContentService.MimeType.JSON);
      
      case 'createPost':
        const postData = JSON.parse(e.parameter.data);
        return ContentService
          .createTextOutput(JSON.stringify(createPost(postData)))
          .setMimeType(ContentService.MimeType.JSON);
      
      case 'schedulePost':
        const scheduleData = JSON.parse(e.parameter.data);
        return ContentService
          .createTextOutput(JSON.stringify(schedulePost(scheduleData)))
          .setMimeType(ContentService.MimeType.JSON);
      
      case 'getScheduledPosts':
        const scheduledPosts = getScheduledPosts();
        Logger.log('getScheduledPosts result: ' + JSON.stringify(scheduledPosts));
        return ContentService
          .createTextOutput(JSON.stringify(scheduledPosts))
          .setMimeType(ContentService.MimeType.JSON);
      
      case 'getPostHistory':
        const postHistory = getPostHistory();
        Logger.log('getPostHistory result: ' + JSON.stringify(postHistory));
        return ContentService
          .createTextOutput(JSON.stringify(postHistory))
          .setMimeType(ContentService.MimeType.JSON);
      
      default:
        throw new Error('不明なアクション: ' + action);
    }
  } catch (error) {
    Logger.log('doPost エラー: ' + error.toString());
    Logger.log('スタックトレース: ' + error.stack);
    return ContentService
      .createTextOutput(JSON.stringify({ error: error.toString(), stack: error.stack }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * HTMLファイルのインクルード処理
 */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

/**
 * アカウント管理
 */
function getAccounts() {
  try {
    const sheet = getSheet('accounts');
    const dataRange = sheet.getDataRange();
    
    // シートが空の場合
    if (dataRange.getNumRows() <= 1) {
      return [];
    }
    
    const data = dataRange.getValues();
    const headers = data[0];
    const accounts = [];
    
    for (let i = 1; i < data.length; i++) {
      const account = {};
      headers.forEach((header, index) => {
        account[header] = data[i][index];
      });
      accounts.push(account);
    }
    
    return accounts;
  } catch (error) {
    Logger.log('getAccounts エラー: ' + error.toString());
    return [];
  }
}

function addAccount(accountData) {
  const sheet = getSheet('accounts');
  const id = Utilities.getUuid();
  const now = new Date().toISOString();
  
  const rowData = [
    id,
    accountData.name,
    accountData.username,
    accountData.accessToken,
    accountData.refreshToken || '',
    accountData.tokenExpiry,
    'active',
    accountData.avatar || '',
    now,
    now
  ];
  
  sheet.appendRow(rowData);
  
  return {
    id: id,
    name: accountData.name,
    username: accountData.username,
    status: 'active',
    createdAt: now
  };
}

/**
 * 投稿管理
 */
function createPost(postData) {
  // Threads API への投稿処理
  const account = getAccountById(postData.accountId);
  if (!account) {
    throw new Error('アカウントが見つかりません');
  }
  
  // Step 1: メディアコンテナ作成
  const containerData = {
    'media_type': postData.mediaType,
    'access_token': account.accessToken
  };
  
  if (postData.text) containerData.text = postData.text;
  if (postData.imageUrl) containerData.image_url = postData.imageUrl;
  if (postData.videoUrl) containerData.video_url = postData.videoUrl;
  if (postData.replyControl) containerData.reply_control = postData.replyControl;
  
  const containerResponse = UrlFetchApp.fetch(
    `https://graph.threads.net/v1.0/${account.username}/threads`,
    {
      method: 'POST',
      payload: containerData
    }
  );
  
  const containerResult = JSON.parse(containerResponse.getContentText());
  
  if (containerResponse.getResponseCode() !== 200) {
    throw new Error('メディアコンテナの作成に失敗しました: ' + containerResult.error.message);
  }
  
  // Step 2: 投稿公開
  const publishResponse = UrlFetchApp.fetch(
    `https://graph.threads.net/v1.0/${account.username}/threads_publish`,
    {
      method: 'POST',
      payload: {
        'creation_id': containerResult.id,
        'access_token': account.accessToken
      }
    }
  );
  
  const publishResult = JSON.parse(publishResponse.getContentText());
  
  if (publishResponse.getResponseCode() !== 200) {
    throw new Error('投稿の公開に失敗しました: ' + publishResult.error.message);
  }
  
  // 投稿履歴に保存
  savePostHistory({
    accountId: account.id,
    accountName: account.name,
    content: postData,
    threadsPostId: publishResult.id,
    status: 'published',
    publishedAt: new Date().toISOString()
  });
  
  return {
    success: true,
    postId: publishResult.id
  };
}

function schedulePost(scheduleData) {
  const sheet = getSheet('scheduled_posts');
  const id = Utilities.getUuid();
  const now = new Date().toISOString();
  
  const rowData = [
    id,
    scheduleData.accountId,
    scheduleData.accountName,
    JSON.stringify(scheduleData.content),
    scheduleData.scheduledTime,
    'pending',
    now,
    now,
    ''
  ];
  
  sheet.appendRow(rowData);
  
  return {
    id: id,
    status: 'scheduled',
    scheduledTime: scheduleData.scheduledTime
  };
}

function getScheduledPosts() {
  try {
    const sheet = getSheet('scheduled_posts');
    const dataRange = sheet.getDataRange();
    
    // シートが空の場合
    if (dataRange.getNumRows() <= 1) {
      return [];
    }
    
    const data = dataRange.getValues();
    const headers = data[0];
    const posts = [];
    
    for (let i = 1; i < data.length; i++) {
      const post = {};
      headers.forEach((header, index) => {
        if (header === 'content') {
          try {
            post[header] = JSON.parse(data[i][index] || '{}');
          } catch (e) {
            post[header] = {};
          }
        } else {
          post[header] = data[i][index];
        }
      });
      posts.push(post);
    }
    
    return posts;
  } catch (error) {
    Logger.log('getScheduledPosts エラー: ' + error.toString());
    return [];
  }
}

function getPostHistory() {
  try {
    const sheet = getSheet('post_history');
    const dataRange = sheet.getDataRange();
    
    // シートが空の場合
    if (dataRange.getNumRows() <= 1) {
      return [];
    }
    
    const data = dataRange.getValues();
    const headers = data[0];
    const posts = [];
    
    for (let i = 1; i < data.length; i++) {
      const post = {};
      headers.forEach((header, index) => {
        if (header === 'content') {
          try {
            post[header] = JSON.parse(data[i][index] || '{}');
          } catch (e) {
            post[header] = {};
          }
        } else {
          post[header] = data[i][index];
        }
      });
      posts.push(post);
    }
    
    return posts;
  } catch (error) {
    Logger.log('getPostHistory エラー: ' + error.toString());
    return [];
  }
}

/**
 * ユーティリティ関数
 */
function getSheet(sheetName) {
  try {
    // SPREADSHEET_IDが設定されていない場合は自動作成
    if (!CONFIG.SPREADSHEET_ID || CONFIG.SPREADSHEET_ID === 'null' || CONFIG.SPREADSHEET_ID === '') {
      Logger.log('SPREADSHEET_IDが設定されていません。新しいスプレッドシートを作成します。');
      const spreadsheetId = setupSpreadsheet();
      PropertiesService.getScriptProperties().setProperty('SPREADSHEET_ID', spreadsheetId);
      // CONFIGを更新
      CONFIG.SPREADSHEET_ID = spreadsheetId;
    }
    
    const spreadsheet = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
    let sheet = spreadsheet.getSheetByName(sheetName);
    
    if (!sheet) {
      sheet = spreadsheet.insertSheet(sheetName);
      initializeSheet(sheet, sheetName);
    }
    
    return sheet;
  } catch (error) {
    Logger.log('getSheet エラー: ' + error.toString());
    Logger.log('SPREADSHEET_ID: ' + CONFIG.SPREADSHEET_ID);
    throw new Error('スプレッドシートにアクセスできません: ' + error.toString());
  }
}

function initializeSheet(sheet, sheetName) {
  let headers = [];
  
  switch (sheetName) {
    case 'accounts':
      headers = ['id', 'name', 'username', 'accessToken', 'refreshToken', 'tokenExpiry', 'status', 'avatar', 'createdAt', 'updatedAt'];
      break;
    case 'scheduled_posts':
      headers = ['id', 'accountId', 'accountName', 'content', 'scheduledTime', 'status', 'createdAt', 'updatedAt', 'error'];
      break;
    case 'post_history':
      headers = ['id', 'accountId', 'accountName', 'content', 'threadsPostId', 'status', 'publishedAt', 'createdAt', 'error'];
      break;
  }
  
  if (headers.length > 0) {
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  }
}

function getAccountById(accountId) {
  const accounts = getAccounts();
  return accounts.find(account => account.id === accountId);
}

function savePostHistory(postData) {
  const sheet = getSheet('post_history');
  const id = Utilities.getUuid();
  const now = new Date().toISOString();
  
  const rowData = [
    id,
    postData.accountId,
    postData.accountName,
    JSON.stringify(postData.content),
    postData.threadsPostId || '',
    postData.status,
    postData.publishedAt || now,
    now,
    postData.error || ''
  ];
  
  sheet.appendRow(rowData);
}

/**
 * スケジュール実行用のトリガー関数
 */
function processScheduledPosts() {
  const scheduledPosts = getScheduledPosts();
  const now = new Date();
  
  scheduledPosts.forEach(post => {
    if (post.status === 'pending' && new Date(post.scheduledTime) <= now) {
      try {
        const result = createPost({
          accountId: post.accountId,
          mediaType: post.content.mediaType,
          text: post.content.text,
          imageUrl: post.content.imageUrl,
          videoUrl: post.content.videoUrl,
          replyControl: post.content.replyControl
        });
        
        // スケジュール投稿のステータスを更新
        updateScheduledPostStatus(post.id, 'published');
        
      } catch (error) {
        Logger.log('スケジュール投稿エラー: ' + error.toString());
        updateScheduledPostStatus(post.id, 'failed', error.toString());
      }
    }
  });
}

function updateScheduledPostStatus(postId, status, error = '') {
  const sheet = getSheet('scheduled_posts');
  const data = sheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === postId) {
      sheet.getRange(i + 1, 6).setValue(status); // status column
      sheet.getRange(i + 1, 8).setValue(new Date().toISOString()); // updatedAt column
      if (error) {
        sheet.getRange(i + 1, 9).setValue(error); // error column
      }
      break;
    }
  }
}

/**
 * 初期設定関数
 */
function setupSpreadsheet() {
  const spreadsheet = SpreadsheetApp.create('Threads投稿マネージャー - データ');
  const spreadsheetId = spreadsheet.getId();
  
  PropertiesService.getScriptProperties().setProperty('SPREADSHEET_ID', spreadsheetId);
  
  Logger.log('スプレッドシートが作成されました: ' + spreadsheetId);
  Logger.log('スプレッドシートURL: ' + spreadsheet.getUrl());
  
  return spreadsheetId;
}

/**
 * トリガー設定
 */
function setupTriggers() {
  // 既存のトリガーを削除
  ScriptApp.getProjectTriggers().forEach(trigger => {
    ScriptApp.deleteTrigger(trigger);
  });
  
  // 5分おきにスケジュール投稿をチェック
  ScriptApp.newTrigger('processScheduledPosts')
    .timeBased()
    .everyMinutes(5)
    .create();
  
  Logger.log('トリガーが設定されました');
}// Test comment for GitHub Actions trigger
// GitHub Actions test - Thu Jun 12 21:56:30 JST 2025
// Develop branch test - Thu Jun 12 22:04:28 JST 2025
