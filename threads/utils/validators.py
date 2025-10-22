import re
from .exceptions import ValidationError

def validate_post_text(text: str) -> bool:
    if not text:
        return True
    if len(text) > 500:
        raise ValidationError("投稿テキストは500文字以内である必要があります")
    return True

def validate_media_url(url: str) -> bool:
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if not url_pattern.match(url):
        raise ValidationError("無効なURLです")
    return True
