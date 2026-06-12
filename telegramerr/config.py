import json
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = "TBD"
    OVERSEERR_URL: str = "http://localhost:5055"
    OVERSEERR_API_KEY: str = "TBD"
    USER_MAPPING: str = "{}"  # JSON string {"telegram_id": "overseerr_id"}
    BOT_LANGUAGE: str = "es"
    POLLING_INTERVAL: int = 60
    LOG_LEVEL: str = "INFO"
    
    @property
    def get_user_mapping(self) -> dict[int, int]:
        try:
            raw_map = json.loads(self.USER_MAPPING)
            return {int(k): int(v) for k, v in raw_map.items()}
        except Exception as e:
            print(f"Error parsing USER_MAPPING: {e}")
            return {}

    class Config:
        env_file = ".env"

settings = Settings()
