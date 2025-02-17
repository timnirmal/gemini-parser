<p align="center">
  <img src="https://github.com/timnirmal/gemini-parser/blob/master/img.png?raw=true" alt="gemini-parser" width="80%"/>
</p>

<h1 align="center">🚀 gemini-parser</h1>
<h3 align="center">Seamless Document Processing with Google Gemini API</h3>

<p align="center">
  <b>Convert, extract, and process documents effortlessly with AI-powered precision.</b>
</p>

<br>

## ✨ What is gemini-parser?

**gemini-parser** is a Python library that simplifies document processing using the **Google Gemini API**.  
It enables developers to **transcribe PDFs**, **extract structured data**, and **summarize large documents** with ease.  
Whether you're working with **local files, URLs, or batch processing**, this library ensures efficiency and automation.

<br>

## 🎯 Why choose gemini-parser?

✅ **AI-Powered Processing** – Uses Google Gemini API for intelligent document parsing.  
📂 **Handles Large Files** – Process documents up to **20GB** effortlessly.  
⚡ **Fast & Optimized** – Smart caching for efficient operations.  
📑 **Multi-Format Support** – Works with **PDF, CSV, HTML, XML, TXT, DOC**, and more.  
🔄 **Flexible Input Options** – Process files from **local storage, folders, or URLs** seamlessly.  

<br>


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
