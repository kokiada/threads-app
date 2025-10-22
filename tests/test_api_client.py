import pytest
from unittest.mock import Mock, patch
from threads.api.threads_client import ThreadsAPIClient
from threads.utils.exceptions import ThreadsAPIError

class TestThreadsAPIClient:
    @pytest.fixture
    def client(self):
        return ThreadsAPIClient(access_token="test_token_123")
    
    @patch('threads.api.threads_client.requests.Session.request')
    def test_create_media_container_text(self, mock_request, client):
        """テキスト投稿のメディアコンテナ作成テスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "container_123"}
        mock_request.return_value = mock_response
        
        result = client.create_media_container(
            "user_123",
            "TEXT",
            text="テスト投稿"
        )
        assert result == "container_123"
    
    @patch('threads.api.threads_client.requests.Session.request')
    def test_publish_post(self, mock_request, client):
        """投稿公開のテスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "post_123"}
        mock_request.return_value = mock_response
        
        result = client.publish_post("user_123", "container_123")
        assert result == "post_123"
    
    @patch('threads.api.threads_client.requests.Session.request')
    def test_api_error(self, mock_request, client):
        """APIエラーのテスト"""
        import requests
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Server Error")
        mock_request.return_value = mock_response
        
        with pytest.raises(ThreadsAPIError):
            client.create_media_container("user_123", "TEXT", text="テスト")
    
    @patch('threads.api.threads_client.requests.Session.request')
    def test_get_publishing_limit(self, mock_request, client):
        """投稿制限取得のテスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"quota_usage": 10, "config": {"quota_total": 250}}]
        }
        mock_request.return_value = mock_response
        
        result = client.get_publishing_limit("user_123")
        assert result["data"][0]["quota_usage"] == 10
