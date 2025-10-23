import cloudinary
import cloudinary.uploader
import os
from typing import Optional

# Cloudinary設定
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_file(file_path: str, resource_type: str = "auto") -> Optional[str]:
    """
    ファイルをCloudinaryにアップロード
    
    Args:
        file_path: アップロードするファイルのパス
        resource_type: "image", "video", "auto"
    
    Returns:
        アップロードされたファイルのURL
    """
    try:
        result = cloudinary.uploader.upload(
            file_path,
            resource_type=resource_type
        )
        return result.get("secure_url")
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return None
