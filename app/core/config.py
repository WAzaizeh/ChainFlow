from dotenv import load_dotenv
import os

# Load environment variables at module level
load_dotenv()

class Settings:
    # App settings
    APP_NAME = "Dera Manager"
    APP_URL = os.getenv("APP_URL", "http://localhost:5001")
    
    # Appwrite settings
    APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
    APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID", "YOUR_PROJECT_ID")
    APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY", "")
    
    # Database settings
    TASKS_DATABASE_ID = os.getenv("TASKS_DATABASE_ID")
    INVENTORY_DATABASE_ID = os.getenv("INVENTORY_DATABASE_ID")
    
    # Auth settings
    OAUTH_SCOPES = ["openid", "email"]
    
    @property
    def oauth_success_url(self):
        return f"{self.APP_URL}/oauth/google"
    
    @property
    def oauth_failure_url(self):
        return f"{self.APP_URL}/login?failed=1"

# Create a global settings instance
settings = Settings()