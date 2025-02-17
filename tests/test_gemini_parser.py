import os
from pathlib import Path
from gemini_parser import DocumentProcessor
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
assert API_KEY, "API key not found in environment variables."

processor = DocumentProcessor(api_key=API_KEY, model_name="gemini-1.5-flash-002")

TEST_FOLDER = Path("test_data")
OUTPUT_FOLDER = Path("output")

def run_test(test_func):
    print(f"\n--- Running {test_func.__name__} ---")
    try:
        test_func()
        print(f"✅ {test_func.__name__} passed")
    except AssertionError as e:
        print(f"❌ {test_func.__name__} failed: {e}")
    except Exception as e:
        print(f"❌ {test_func.__name__} encountered an error: {e}")


def test_single_small_pdf():
    file_path = TEST_FOLDER / "small_file.pdf"
    result = processor.process_file(file_path)
    assert result, f"No output for small PDF: {file_path}"


def test_single_pdf_with_cache():
    file_path = TEST_FOLDER / "small_file.pdf"
    result = processor.process_file(file_path, use_cache=True, cache_ttl=1)
    assert result, f"No output for PDF with caching: {file_path}"


def test_multiple_pdfs():
    files = [TEST_FOLDER / "small_file.pdf", TEST_FOLDER / "another_file.pdf"]
    result = processor.process_multiple_files(files)
    assert result, f"No output for multiple PDFs: {files}"


def test_folder_of_pdfs():
    processor.process_folder(TEST_FOLDER, OUTPUT_FOLDER)
    output_files = list(OUTPUT_FOLDER.glob("*.md"))
    assert len(output_files) > 0, f"No output for folder: {TEST_FOLDER}"


def test_folder_with_cache():
    processor.process_folder(TEST_FOLDER, OUTPUT_FOLDER, use_cache=True, cache_ttl=2)
    output_files = list(OUTPUT_FOLDER.glob("*.md"))
    assert len(output_files) > 0, f"No output for folder with caching: {TEST_FOLDER}"


def test_pdf_from_url():
    url = "https://www.nasa.gov/wp-content/uploads/static/history/alsj/a17/A17_FlightPlan.pdf"
    result = processor.process_from_url(url)
    assert result, f"No output from URL: {url}"


def test_pdf_from_url_with_cache():
    url = "https://www.nasa.gov/wp-content/uploads/static/history/alsj/a17/A17_FlightPlan.pdf"
    result = processor.process_from_url(url, use_cache=True, cache_ttl=1)
    assert result, f"No output from URL with caching: {url}"


def test_invalid_local_path():
    invalid_path = TEST_FOLDER / "non_existent.pdf"
    result = processor.process_file(invalid_path)
    assert result == "", f"Invalid path processed unexpectedly: {invalid_path}"


def test_invalid_url():
    url = "https://invalid.url/test.pdf"
    result = processor.process_from_url(url)
    assert result == "", f"Invalid URL processed unexpectedly: {url}"


def test_list_caches():
    caches = processor.list_caches()
    assert isinstance(caches, list), "Caches not listed properly."


def test_delete_cache():
    file_path = TEST_FOLDER / "small_file.pdf"
    processor.process_file(file_path, use_cache=True, cache_ttl=1)
    caches = processor.list_caches()
    if caches:
        processor.delete_cache(caches[0].name)


def test_delete_invalid_cache():
    try:
        processor.delete_cache("invalid_cache_name")
    except Exception:
        pass  # Expected error


def test_invalid_mime_type():
    file_path = TEST_FOLDER / "unsupported_file.xyz"
    result = processor.process_file(file_path)
    assert result == "", f"Invalid MIME type processed unexpectedly: {file_path}"


def test_text_file():
    file_path = TEST_FOLDER / "sample.txt"
    result = processor.process_file(file_path)
    assert result, f"No output for text file: {file_path}"


if __name__ == "__main__":
    tests = [
        # test_single_small_pdf,
        test_single_pdf_with_cache,
        # test_multiple_pdfs,
        # test_folder_of_pdfs,
        # test_folder_with_cache,
        test_pdf_from_url,
        test_pdf_from_url_with_cache,
        # test_invalid_local_path,
        # test_invalid_url,
        # test_list_caches,
        # test_delete_cache,
        # test_delete_invalid_cache,
        # test_invalid_mime_type,
        # test_text_file,
    ]

    for test in tests:
        run_test(test)

    print("\n🎉 All tests completed!")


