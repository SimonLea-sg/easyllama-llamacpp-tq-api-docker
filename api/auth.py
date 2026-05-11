from fastapi import HTTPException
from typing import Optional

from config import AppSettings

# Helper function to handle authentication logic
def verify_api_key(app_settings: AppSettings, x_api_key: Optional[str] = None):
    valid_keys = app_settings.api_keys
    if valid_keys:
        if not x_api_key or x_api_key not in valid_keys.split(","):
            raise HTTPException(status_code=401, detail="Invalid API Key")