import logging
import os
import time
import httpx
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tempfile import mkdtemp
from typing import Optional, List, Dict, Union

from tqdm import tqdm
from PyPDF2 import PdfReader, PdfWriter
from google import genai
from google.genai import types

from .utils import get_mime_type
from .file_manager import FileManager
from .caching import CachingManager


class DocumentProcessor:
    """
    A document processor using Google Gemini API.

    Features:
      - Supports multiple file formats (PDF, TXT, CSV, MD, HTML, XML, RTF, etc.)
      - For PDFs: splits the file into chunks to handle token limits, processes chunks in parallel, and merges results.
      - Processes documents from local files or URLs.
      - Supports a user-defined operation type (e.g., "parse", "summarize", "extract") and allows custom prompts.
      - Provides caching utilities (list and delete caches).
    """

    def __init__(
            self,
            api_key: str,
            model_name: str = "gemini-1.5-flash-002",
            default_prompt: str = "Transcribe this document into markdown format preserving layout and formatting. Also, if you find images, describe the given image as well.",
            log_level: str = "INFO",
            allowed_extensions: Optional[Dict[str, str]] = None,
            pages_per_chunk: int = 5,  # Adjust based on token limits (~8000 tokens/request)
            max_threads: int = 4,
            max_retries: int = 2,
            retry_delay: int = 2,
            size_threshold: int = 20 * 1024 * 1024,  # 20MB threshold for non-chunking
    ):
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        logging.basicConfig(level=numeric_level, format="%(asctime)s [%(levelname)s] - %(message)s")
        self.logger = logging.getLogger(self.__class__.__name__)

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.default_prompt = default_prompt
        self.pages_per_chunk = pages_per_chunk
        self.max_threads = max_threads
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.size_threshold = size_threshold

        # Supported file extensions with their MIME types.
        self.allowed_extensions = allowed_extensions or {
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".csv": "text/csv",
            ".md": "text/markdown",
            ".html": "text/html",
            ".xml": "text/xml",
            ".rtf": "text/rtf",
            ".py": "text/x-python",
            ".js": "application/x-javascript",
            ".css": "text/css"
        }

        self.file_manager = FileManager(self.client)
        self.caching_manager = CachingManager(self.client)

    def process_file(
            self,
            file_path: Path,
            operation: str = "parse",
            prompt: Optional[str] = None,
            use_cache: bool = False,
            cache_ttl: Optional[int] = None
    ) -> str:
        """
        Processes a local file.

        :param file_path: Path to the file.
        :param operation: Operation type (e.g., "parse", "summarize", "extract").
        :param prompt: Optional custom prompt. If not provided, default_prompt is used.
        :param use_cache: Whether to use caching.
        :param cache_ttl: Cache TTL in hours.
        :return: The generated text.
        """
        if not file_path.exists():
            self.logger.error(f"File does not exist: {file_path}")
            return ""

        prompt = prompt or self.default_prompt
        ext = file_path.suffix.lower()

        # For caching: create a simple cache key based on filename and operation.
        cache_key = f"{file_path.name}_{operation}"

        if use_cache:
            # Here, you might implement retrieval of cached results if available.
            # For now, we'll assume caching_manager.list_caches() does not support get/store.
            # You can extend CachingManager with your own get_cache/store_cache logic.
            self.logger.info(f"Cache usage requested for {file_path} with key {cache_key}.")

        if ext == ".pdf":
            result = self._process_large_pdf(file_path, operation, prompt)
        else:
            result = self._process_non_pdf(file_path, operation, prompt)

        # Store result in cache if needed (assuming caching_manager supports it).
        if use_cache and result:
            # Example: self.caching_manager.store_cache(cache_key, result, cache_ttl)
            # Since our provided CachingManager doesn't include store/get, this is a placeholder.
            self.logger.info(f"Storing result in cache with key {cache_key} for {cache_ttl} hours.")

        return result

    def process_from_url(
            self,
            url: str,
            operation: str = "parse",
            prompt: Optional[str] = None,
            use_cache: bool = False,
            cache_ttl: Optional[int] = None
    ) -> str:
        """
        Downloads a document from a URL and processes it.

        :param url: URL of the document.
        :param operation: Operation type.
        :param prompt: Optional custom prompt.
        :param use_cache: Whether to use caching.
        :param cache_ttl: Cache TTL in hours.
        :return: The generated text.
        """
        self.logger.info(f"Fetching document from URL: {url}")
        resp = httpx.get(url)
        resp.raise_for_status()

        # Save to a temporary file to process as a local file.
        temp_dir = mkdtemp()
        temp_file = Path(temp_dir) / "remote_file.pdf"
        temp_file.write_bytes(resp.content)

        result = self.process_file(temp_file, operation, prompt, use_cache, cache_ttl)

        temp_file.unlink()
        os.rmdir(temp_dir)
        return result

    def process_multiple_files(
            self,
            file_paths: List[Union[str, Path]],
            operation: str = "parse",
            prompt: Optional[str] = None,
            use_cache: bool = False,
            cache_ttl: Optional[int] = None
    ) -> str:
        """
        Processes multiple files in a single request.

        :param file_paths: List of file paths.
        :param operation: Operation type.
        :param prompt: Optional custom prompt.
        :param use_cache: Whether to use caching.
        :param cache_ttl: Cache TTL in hours.
        :return: Combined result from all files.
        """
        results = []
        for fp in file_paths:
            path_obj = Path(fp)
            result = self.process_file(path_obj, operation, prompt, use_cache, cache_ttl)
            if result:
                results.append(result)
        return "\n\n".join(results)

    def process_folder(
            self,
            folder_path: Path,
            output_dir: Optional[Path] = None,
            out_ext: str = "md",
            operation: str = "parse",
            prompt: Optional[str] = None,
            use_cache: bool = False,
            cache_ttl: Optional[int] = None
    ) -> None:
        """
        Processes all allowed files in a folder and writes output to the output directory.

        :param folder_path: Path to the folder.
        :param output_dir: Directory to save output files (if not provided, uses folder_path).
        :param out_ext: Output file extension.
        :param operation: Operation type.
        :param prompt: Optional custom prompt.
        :param use_cache: Whether to use caching.
        :param cache_ttl: Cache TTL in hours.
        """
        if not folder_path.exists() or not folder_path.is_dir():
            self.logger.error(f"Folder does not exist: {folder_path}")
            return

        output_dir = output_dir or folder_path
        output_dir.mkdir(parents=True, exist_ok=True)
        files = [f for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() in self.allowed_extensions]

        for f in tqdm(files, desc=f"Processing folder {folder_path}"):
            self.logger.info(f"Processing file: {f.name}")
            result_text = self.process_file(f, operation, prompt, use_cache, cache_ttl)
            if result_text:
                out_file = output_dir / f"{f.stem}.{out_ext}"
                out_file.write_text(result_text, encoding="utf-8")
                self.logger.info(f"Saved output to: {out_file}")
            else:
                self.logger.warning(f"No output for {f.name}")

    def list_caches(self) -> List:
        """
        Lists all available caches.
        """
        try:
            caches = self.caching_manager.list_caches()
            return caches
        except Exception as e:
            self.logger.error(f"Failed to list caches: {e}")
            return []

    def delete_cache(self, cache_name: str) -> None:
        """
        Deletes a specific cache by its name.

        :param cache_name: Name of the cache to delete.
        """
        try:
            self.caching_manager.delete_cache(cache_name)
            self.logger.info(f"Cache {cache_name} deleted successfully.")
        except Exception as e:
            self.logger.error(f"Failed to delete cache {cache_name}: {e}")

    # Internal helper methods for PDF processing:

    def _process_large_pdf(self, file_path: Path, operation: str, prompt: str) -> str:
        """
        Splits a large PDF into chunks, processes them in parallel, and merges the results.
        """
        chunk_paths = self._split_pdf(file_path)
        results = [None] * len(chunk_paths)

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_idx = {
                executor.submit(self._process_pdf_chunk, chunk, operation, prompt): i
                for i, chunk in enumerate(chunk_paths)
            }
            for future in tqdm(as_completed(future_to_idx), total=len(future_to_idx), desc="Processing PDF chunks"):
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    self.logger.error(f"Failed processing chunk {chunk_paths[idx]}: {e}")
                    results[idx] = ""

        # Optionally, clean up temporary chunk files
        for chunk in chunk_paths:
            try:
                chunk.unlink()
            except Exception:
                pass

        return "\n\n".join(filter(None, results))

    def _process_pdf_chunk(self, chunk_path: Path, operation: str, prompt: str) -> str:
        """
        Processes a single PDF chunk with retry logic.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                file_bytes = chunk_path.read_bytes()
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[types.Part.from_bytes(data=file_bytes, mime_type="application/pdf"), prompt]
                )
                return response.text
            except Exception as e:
                self.logger.warning(f"Attempt {attempt}/{self.max_retries} failed for {chunk_path}: {e}")
                time.sleep(self.retry_delay)
        return ""

    def _split_pdf(self, file_path: Path) -> List[Path]:
        """
        Splits a PDF file into smaller chunks based on pages_per_chunk.
        """
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        temp_dir = Path(mkdtemp(prefix="pdf_chunks_"))
        chunk_paths = []

        for start in range(0, total_pages, self.pages_per_chunk):
            writer = PdfWriter()
            for i in range(start, min(start + self.pages_per_chunk, total_pages)):
                writer.add_page(reader.pages[i])
            chunk_path = temp_dir / f"{file_path.stem}_chunk_{start // self.pages_per_chunk + 1}.pdf"
            with open(chunk_path, "wb") as cf:
                writer.write(cf)
            chunk_paths.append(chunk_path)

        return chunk_paths

    def _process_non_pdf(self, file_path: Path, operation: str, prompt: str) -> str:
        """
        Processes non-PDF files directly.
        """
        file_bytes = file_path.read_bytes()
        mime_type = get_mime_type(file_path, self.allowed_extensions)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[types.Part.from_bytes(data=file_bytes, mime_type=mime_type), prompt]
        )
        return response.text
