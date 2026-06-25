import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def clean_gemini_storage():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in your .env file.")
        print("Please add it and try again.")
        return

    print("🔑 Authenticating with Gemini API...")
    genai.configure(api_key=api_key)

    print("📂 Fetching files from Gemini storage...")
    try:
        # Get the list of all uploaded files
        files = list(genai.list_files())
        
        if not files:
            print("✨ Your Gemini storage is already clean. No files found.")
            return

        print(f"🗑️ Found {len(files)} file(s). Starting cleanup process...")
        
        deleted_count = 0
        for file in files:
            print(f"  -> Deleting: {file.display_name or 'Unnamed File'} (ID: {file.name})")
            file.delete()
            deleted_count += 1
            
        print(f"\n✅ Successfully deleted {deleted_count} file(s) from Gemini storage!")
        
    except Exception as e:
        print(f"\n❌ An error occurred during cleanup: {e}")

if __name__ == "__main__":
    clean_gemini_storage()
