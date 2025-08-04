from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API = os.getenv("GEMINI_API", "")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "")
SUPABASE_URL = f"http://{os.getenv('SUPABASE_URL')}:8000"
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SMART_PROXY = os.getenv("SMART_PROXY", "")
ERROR_FILE = os.getenv("ERROR_FILE", "")
UPLOAD_FILE = os.getenv("UPLOAD_FILE", "")
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
RESIDENTIAL_PROXY = (
    f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@fr.decodo.com:40000"
)
