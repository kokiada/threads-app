/**
 * Threads 投稿マネージャー - Google Apps Script版
 * メイン処理ファイル
 * Updated: Test with GitHub Secrets configured
 */

// グローバル設定
const CONFIG = {
  SPREADSHEET_ID: PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID'),
  THREADS_CLIENT_ID: PropertiesService.getScriptProperties().getProperty('THREADS_CLIENT_ID'),
  THREADS_CLIENT_SECRET: PropertiesService.getScriptProperties().getProperty('THREADS_CLIENT_SECRET'),
  BASE_URL: 'https://script.google.com/macros/d/' + ScriptApp.getScriptId() + '/exec'
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
 * POST リクエストの処理
 */
function doPost(e) {
  const action = e.parameter.action;
  
  try {
    switch (action) {
      case 'getAccounts':
        return ContentService
          .createTextOutput(JSON.stringify(getAccounts()))
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
        return ContentService
          .createTextOutput(JSON.stringify(getScheduledPosts()))
          .setMimeType(ContentService.MimeType.JSON);
      
      case 'getPostHistory':
        return ContentService
          .createTextOutput(JSON.stringify(getPostHistory()))
          .setMimeType(ContentService.MimeType.JSON);
      
      default:
        throw new Error('不明なアクション: ' + action);
    }
  } catch (error) {
    Logger.log('エラー: ' + error.toString());
    return ContentService
      .createTextOutput(JSON.stringify({ error: error.toString() }))
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
  const sheet = getSheet('accounts');
  const data = sheet.getDataRange().getValues();
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
  const sheet = getSheet('scheduled_posts');
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const posts = [];
  
  for (let i = 1; i < data.length; i++) {
    const post = {};
    headers.forEach((header, index) => {
      if (header === 'content') {
        post[header] = JSON.parse(data[i][index] || '{}');
      } else {
        post[header] = data[i][index];
      }
    });
    posts.push(post);
  }
  
  return posts;
}

function getPostHistory() {
  const sheet = getSheet('post_history');
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const posts = [];
  
  for (let i = 1; i < data.length; i++) {
    const post = {};
    headers.forEach((header, index) => {
      if (header === 'content') {
        post[header] = JSON.parse(data[i][index] || '{}');
      } else {
        post[header] = data[i][index];
      }
    });
    posts.push(post);
  }
  
  return posts;
}

/**
 * ユーティリティ関数
 */
function getSheet(sheetName) {
  const spreadsheet = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
  let sheet = spreadsheet.getSheetByName(sheetName);
  
  if (!sheet) {
    sheet = spreadsheet.insertSheet(sheetName);
    initializeSheet(sheet, sheetName);
  }
  
  return sheet;
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
