import os
from pathlib import Path
from gemini_parser import DocumentProcessor
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
assert API_KEY, "API key not found in environment variables."

processor = DocumentProcessor(api_key=API_KEY, model_name="gemini-1.5-flash-002")

print("My files:")
for f in processor.client.files.list():
    print("  ", f.name)
