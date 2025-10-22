# Scripts

このディレクトリには開発・テスト用のスクリプトが含まれています。

## スクリプト一覧

### init_db.py
データベースを初期化するスクリプト。

```bash
python scripts/init_db.py
```

### test_setup.py
基本セットアップの動作確認テスト。

```bash
python scripts/test_setup.py
```

### test_services.py
サービス層の動作確認テスト。

```bash
python scripts/test_services.py
```

## 使用方法

すべてのスクリプトはプロジェクトルートから実行してください：

```bash
cd /home/koki/work/threads
source venv/bin/activate
python scripts/<script_name>.py
```
