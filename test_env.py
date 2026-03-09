import os
from dotenv import load_dotenv

load_dotenv()

print("Project:", os.getenv("GOOGLE_CLOUD_PROJECT"))
print("Location:", os.getenv("GOOGLE_CLOUD_LOCATION"))

try:
    import google.genai
    print("google-genai imported successfully")
except Exception as e:
    print("google-genai import failed:", e)

try:
    import google.adk
    print("google-adk imported successfully")
except Exception as e:
    print("google-adk import failed:", e)
