<p align="center">
  <img src="https://github.com/timnirmal/gemini-parser/blob/master/img.png?raw=true" alt="gemini-parser" width="80%"/>
</p>

<h1 align="center">gemini-parser</h1>
<p align="center">
  Seamless Document Processing with Google Gemini API
</p>

---

**gemini-parser** is a Python library that simplifies document processing using the **Google Gemini API**. From **transcribing PDFs** and **extracting structured data** to **summarizing large documents**, it’s designed to handle it all – efficiently and effortlessly.

---

## 🎯 Why gemini-parser?

- 🚀 **Effortless Document Processing**: Upload, parse, and extract insights from PDFs and text files.
- ⚡ **Handles Large Files**: Process files up to 20GB with Gemini’s File API.
- 🔄 **Caching for Speed**: Cache document content for faster future processing.
- 📦 **All-in-One Library**: Local files, URLs, and folder batch processing in a single package.
- 🛡️ **Robust & Reliable**: Built-in error handling, logging, and test coverage.

---

## 📦 Installation

```bash
pip install gemini-parser


---

## **Usage**

### **Quickstart Example**

```python
from gemini_parser import DocumentProcessor
from pathlib import Path
import os

# Initialize processor with API key
processor = DocumentProcessor(api_key=os.getenv("GEMINI_API_KEY"))

# Process a single PDF file
result = processor.process_file(Path("path/to/document.pdf"))
print(result)

# Process from a URL
url_result = processor.process_from_url("https://example.com/document.pdf")
print(url_result)

# Process all files in a folder
processor.process_folder(Path("path/to/folder"))

# List all caches
caches = processor.list_caches()
print(caches)

# Delete a cache
processor.delete_cache("cachedContentID")
```

---

## **Configuration**

You can customize key parameters when initializing the `DocumentProcessor`:

- **`api_key`**: Your Gemini API key.
- **`model_name`**: The Gemini model (e.g., `gemini-1.5-flash-002`).
- **`prompt`**: The default processing prompt.
- **`log_level`**: Logging level (`INFO`, `DEBUG`, etc.).

---

## **API Reference**

### `DocumentProcessor`

- **`process_file(file_path, use_cache=False, cache_ttl=None)`**: Processes a local file.
- **`process_from_url(url, use_cache=False, cache_ttl=None)`**: Processes a document from a URL.
- **`process_multiple_files(file_paths, use_cache=False, cache_ttl=None)`**: Processes multiple files.
- **`process_folder(folder_path, output_dir=None, out_ext="md", use_cache=False, cache_ttl=None)`**: Processes all files in a folder.
- **`list_caches()`**: Lists all available caches.
- **`delete_cache(cache_name)`**: Deletes a cache by name.

### `FileManager`

- **`upload_file(file_or_path, mime_type)`**: Uploads files to Gemini.
- **`list_files()`**: Lists all uploaded files.
- **`get_file(file_name)`**: Gets metadata of a file.
- **`delete_file(file_name)`**: Deletes an uploaded file.

### `CachingManager`

- **`create_cache(model_name, contents, system_instruction)`**: Creates a new cache.
- **`generate_with_cache(model_name, cached_content_name, prompt)`**: Generates content using a cache.
- **`list_caches()`**: Lists all cached content.
- **`update_cache_ttl(cache_name, hours)`**: Updates the cache TTL.
- **`delete_cache(cache_name)`**: Deletes a cache.

---

## **Testing**

Your library includes `pytest`-based tests in the `tests/` folder. Run them with:

```bash
pytest tests/
```

---

## **Requirements**

- Python 3.8+
- `tqdm`
- `PyPDF2`
- `google-genai`
- `python-dotenv`
- `httpx`

---

## **Project Structure**

```
gemini-parser/
│
├── gemini_parser/
│   ├── document_processor.py
│   ├── file_manager.py
│   ├── caching.py
│   ├── utils.py
│
├── tests/
│   ├── test_gemini_parser.py
│
├── setup.py
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## **License**

This project is licensed under the MIT License.

---

## **Contributing**

Contributions are welcome! Please fork this repository, create a new branch, and submit a pull request.

---

## **Author**

Developed by **Thimira Nirmal**  
📧 [timnirmal@gmail.com](mailto:timnirmal@gmail.com)  
🌐 [GitHub](https://github.com/timnirmal) | [Website](https://www.timnirmal.com)
```
