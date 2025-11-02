import requests
import time
from typing import Dict, List, Optional
from ..utils.exceptions import ThreadsAPIError, RateLimitError, TokenExpiredError
from ..utils.logger import logger

class ThreadsAPIClient:
    BASE_URL = "https://graph.threads.net/v1.0"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None, retries: int = 3) -> Dict:
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}
        data = data or {}
        
        # access_tokenをdataに含める（POST）またはparams（GET）
        if method == "POST":
            data["access_token"] = self.access_token
        else:
            params["access_token"] = self.access_token
        
        logger.info(f"API Request: {method} {url}")
        logger.info(f"Request data: {data}")
        
        for attempt in range(retries):
            try:
                response = self.session.request(method, url, params=params, data=data)
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response body: {response.text}")
                
                if response.status_code == 429:
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limit hit, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                if response.status_code == 401:
                    logger.error("Access token expired")
                    raise TokenExpiredError("Access token expired")
                
                if response.status_code >= 400:
                    logger.error(f"API Error: {response.text}")
                
                response.raise_for_status()
                logger.info(f"API Request successful: {endpoint}")
                return response.json()
            
            except requests.exceptions.HTTPError as e:
                logger.error(f"API request failed (attempt {attempt + 1}/{retries}): {str(e)}")
                if attempt == retries - 1:
                    raise ThreadsAPIError(f"API request failed: {str(e)}")
                time.sleep(2 ** attempt)
        
        logger.error("Max retries exceeded")
        raise ThreadsAPIError("Max retries exceeded")
    
    def create_media_container(self, user_id: str, media_type: str, text: str = None, 
                              image_url: str = None, video_url: str = None, 
                              children: List[str] = None) -> str:
        endpoint = f"{user_id}/threads"
        data = {"media_type": media_type}
        
        if text:
            data["text"] = text
        if image_url:
            data["image_url"] = image_url
        if video_url:
            data["video_url"] = video_url
        if children:
            data["children"] = children
        
        result = self._request("POST", endpoint, data=data)
        return result.get("id")
    
    def publish_post(self, user_id: str, creation_id: str) -> str:
        endpoint = f"{user_id}/threads_publish"
        data = {"creation_id": creation_id}
        result = self._request("POST", endpoint, data=data)
        return result.get("id")
    
    def get_user_threads(self, user_id: str, fields: List[str] = None) -> List[Dict]:
        endpoint = f"{user_id}/threads"
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        result = self._request("GET", endpoint, params=params)
        return result.get("data", [])
    
    def get_media_insights(self, media_id: str, metrics: List[str]) -> Dict:
        endpoint = f"{media_id}/insights"
        params = {"metric": ",".join(metrics)}
        result = self._request("GET", endpoint, params=params)
        return result
    
    def get_user_insights(self, user_id: str, metrics: List[str], since: int = None, until: int = None) -> Dict:
        endpoint = f"{user_id}/threads_insights"
        params = {"metric": ",".join(metrics)}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        result = self._request("GET", endpoint, params=params)
        return result
    
    def refresh_access_token(self) -> Dict:
        endpoint = "refresh_access_token"
        params = {"grant_type": "th_refresh_token", "access_token": self.access_token}
        result = self._request("GET", endpoint, params=params)
        return result
    
    def get_publishing_limit(self, user_id: str) -> Dict:
        endpoint = f"{user_id}/threads_publishing_limit"
        result = self._request("GET", endpoint)
        return result
