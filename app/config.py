"""
Configuration for Room API
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application Settings"""
    
    # API Key for authentication
    api_key: str = "change-me-in-production"
    
    # Prosody HTTP API URL
    prosody_url: str = "http://prosody:5280"
    
    # MUC domain
    muc_domain: str = "muc.meet.yourdomain.com"
    
    # Alternative MUC domain (conference alias)
    muc_domain_alt: Optional[str] = "conference.meet.yourdomain.com"
    
    # App settings
    app_title: str = "Prosody Participant Count Hook"
    app_version: str = "1.0.0"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = "PPCH_"  # Add prefix support if needed, but for now we map manually in docker-compose or rely on direct names if they match field names. 
        # Actually, Pydantic BaseSettings reads case-insensitive by default if not specified otherwise, but let's stick to the plan of renaming vars.
        # The previous code didn't have explicit Field(alias=...) so it relied on variable names matching or case-insensitive match.
        # Let's check how it was used.
        # The original code:
        # api_key: str = "change-me-in-production"
        # ...
        # env_file = ".env"
        # case_sensitive = False
        
        # If I want to support PPCH_API_KEY, I should probably use Field(alias='PPCH_API_KEY') or just rely on the user setting 'API_KEY' in env if that's how it worked, 
        # BUT the docker-compose mapped PROSPYDOOR_API_KEY to API_KEY.
        # So inside the app it expects API_KEY.
        # Wait, the docker-compose said:
        # environment:
        #   - API_KEY=${PROSPYDOOR_API_KEY}
        
        # So the python app sees "API_KEY".
        # So I don't strictly need to change the python code for env vars IF I keep the internal names the same.
        # However, I should update the app_title.
        
settings = Settings()
