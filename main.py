# example_usage.py
import os
from pathlib import Path
from gemini_parser import DocumentProcessor, FileManager, CachingManager
from dotenv import load_dotenv

load_dotenv()

def main():
    # 1) Create the main DocumentProcessor
    parser = DocumentProcessor(
        api_key=os.getenv("GEMINI_API_KEY"),
        model_name="gemini-2.0-flash",
        prompt="Summarize this document in detail, focusing on tables and images.",
        pages_per_chunk=5,
        max_threads=2,
        max_retries=3,
        retry_delay=2,
        # log_level="DEBUG"
    )

    # # 2) Process a single folder
    # parser.process_folder(Path("./some_local_folder"), output_dir=Path("./results"))

    # 3) Process from URL
    url_result = parser.process_from_url("https://www.nasa.gov/wp-content/uploads/static/history/alsj/a17/A17_FlightPlan.pdf")
    print("URL result:\n", url_result[:500], "...")

    # # 4) Work with FileManager for direct file operations (File API)
    # fm = FileManager(parser.client)
    # uploaded = fm.upload_file("./some_big_document.pdf", config={"mime_type": "application/pdf"})
    # # ... do something with the uploaded file, or delete it
    # fm.delete_file(uploaded.name)
    #
    # # 5) Use CachingManager for caching
    # cm = CachingManager(parser.client)
    # cache_obj = cm.create_cache(model_name="gemini-2.0-flash", contents=[uploaded], system_instruction="You are an expert on flight plans.")
    # # generate new content from the cache
    # new_text = cm.generate_with_cache(model_name="gemini-2.0-flash", cached_content_name=cache_obj.name, prompt="Please summarize again with more emphasis on safety.")
    # print("New text from cache:\n", new_text)

    # # cleanup
    # cm.delete_cache(cache_obj.name)

if __name__ == "__main__":
    main()
