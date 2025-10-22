import pytest
from threads.utils.crypto import encrypt_token, decrypt_token
from threads.utils.validators import validate_post_text, validate_media_url
from threads.utils.exceptions import ValidationError

class TestCrypto:
    def test_encrypt_decrypt(self):
        """暗号化と復号化のテスト"""
        token = "test_token_12345"
        encrypted = encrypt_token(token)
        decrypted = decrypt_token(encrypted)
        assert decrypted == token
        assert encrypted != token

class TestValidators:
    def test_validate_post_text_valid(self):
        """有効な投稿テキストのバリデーション"""
        text = "これは有効な投稿です"
        assert validate_post_text(text) == True
    
    def test_validate_post_text_too_long(self):
        """500文字超過のテキストバリデーション"""
        text = "あ" * 501
        with pytest.raises(ValidationError):
            validate_post_text(text)
    
    def test_validate_media_url_valid(self):
        """有効なメディアURLのバリデーション"""
        url = "https://example.com/image.jpg"
        assert validate_media_url(url) == True
    
    def test_validate_media_url_invalid(self):
        """無効なメディアURLのバリデーション"""
        url = "not_a_url"
        with pytest.raises(ValidationError):
            validate_media_url(url)
