#!/usr/bin/env python
"""セットアップ動作確認スクリプト"""
import sys

def test_imports():
    print("1. モジュールインポートテスト...")
    try:
        from threads.models import Account, PostGroup, Post, Schedule
        from threads.utils.crypto import encrypt_token, decrypt_token
        from threads.utils.validators import validate_post_text, validate_media_url
        from threads.api.threads_client import ThreadsAPIClient
        print("   ✓ すべてのモジュールが正常にインポートされました")
        return True
    except Exception as e:
        print(f"   ✗ インポートエラー: {e}")
        return False

def test_crypto():
    print("\n2. 暗号化機能テスト...")
    try:
        from threads.utils.crypto import encrypt_token, decrypt_token
        test_token = "test_access_token_12345"
        encrypted = encrypt_token(test_token)
        decrypted = decrypt_token(encrypted)
        assert test_token == decrypted
        print(f"   ✓ 暗号化/復号化が正常に動作しました")
        print(f"   元のトークン: {test_token}")
        print(f"   暗号化後: {encrypted[:50]}...")
        return True
    except Exception as e:
        print(f"   ✗ 暗号化エラー: {e}")
        return False

def test_validators():
    print("\n3. バリデーション機能テスト...")
    try:
        from threads.utils.validators import validate_post_text, validate_media_url
        
        # テキストバリデーション
        assert validate_post_text("短いテキスト") == True
        assert validate_post_text("a" * 500) == True
        assert validate_post_text("a" * 501) == False
        
        # URLバリデーション
        assert validate_media_url("https://example.com/image.jpg") == True
        assert validate_media_url("invalid_url") == False
        
        print("   ✓ バリデーション機能が正常に動作しました")
        return True
    except Exception as e:
        print(f"   ✗ バリデーションエラー: {e}")
        return False

def test_database():
    print("\n4. データベース接続テスト...")
    try:
        from threads.models import init_db, engine
        init_db()
        with engine.connect() as conn:
            print("   ✓ データベース接続が正常に確立されました")
        return True
    except Exception as e:
        print(f"   ✗ データベースエラー: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Phase 0-2 セットアップ動作確認")
    print("=" * 60)
    
    results = []
    results.append(test_imports())
    results.append(test_crypto())
    results.append(test_validators())
    results.append(test_database())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ すべてのテストが成功しました！")
        print("=" * 60)
        sys.exit(0)
    else:
        print("✗ 一部のテストが失敗しました")
        print("=" * 60)
        sys.exit(1)
