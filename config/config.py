from dotenv import load_dotenv
import os

load_dotenv()


GEMINI_API = os.getenv("GEMINI_API")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SMART_PROXY = os.getenv("SMART_PROXY")
