from dotenv import load_dotenv
import os

# Load environment variables at module level
load_dotenv()

class Settings:
    # App settings
    APP_NAME = "Dera Manager"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(8080 if os.getenv("DEV_ENV") else os.getenv("PORT", 5001))
    APP_URL = os.getenv("APP_URL", f"http://localhost:{PORT}")
    
    # Appwrite settings
    APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
    APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID", "YOUR_PROJECT_ID")
    APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY", "")
    
    # Database settings
    TASKS_DATABASE_ID = os.getenv("TASKS_DATABASE_ID")
    INVENTORY_DATABASE_ID = os.getenv("INVENTORY_DATABASE_ID")
    
    # Auth settings
    OAUTH_SCOPES = ["openid", "email"]

    # GitHub settings
    GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", None)
    
    @property
    def oauth_success_url(self):
        return f"{self.APP_URL}/oauth/google"
    
    @property
    def oauth_failure_url(self):
        return f"{self.APP_URL}/login?failed=1"

# Create a global settings instance
settings = Settings()