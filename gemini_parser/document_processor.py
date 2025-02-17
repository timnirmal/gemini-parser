import logging
import httpx
import io
from pathlib import Path
from typing import List, Union, Optional
from google import genai
from tqdm import tqdm
from .file_manager import FileManager
from .caching import CachingManager


class DocumentProcessor:
    """
    A document processor using Gemini's File API and caching, with cache management utilities and error handling.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash",
        prompt: str = "Transcribe this document into text format preserving layout and formatting.",
        log_level: str = "INFO",
    ):
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        logging.basicConfig(level=numeric_level, format="%(asctime)s [%(levelname)s] - %(message)s")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.prompt = prompt
        self.file_manager = FileManager(self.client)
        self.caching_manager = CachingManager(self.client)

    def process_file(self, file_path: Path, use_cache: bool = False, cache_ttl: Optional[float] = None) -> str:
        if not file_path.exists() or not file_path.is_file():
            self.logger.error(f"File does not exist: {file_path}")
            return ""

        try:
            mime_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else "text/plain"
            uploaded_file = self.file_manager.upload_file(file_path, mime_type=mime_type)

            if use_cache:
                cache = self.caching_manager.create_cache(
                    model_name=self.model_name,
                    contents=[uploaded_file],
                    system_instruction="You are processing documents efficiently."
                )
                if cache_ttl:
                    self.caching_manager.update_cache_ttl(cache.name, hours=cache_ttl)
                response = self.caching_manager.generate_with_cache(self.model_name, cache.name, self.prompt)
            else:
                response = self.client.models.generate_content(model=self.model_name, contents=[uploaded_file, self.prompt])

            return response.text
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            return ""

    def process_from_url(self, url: str, use_cache: bool = False, cache_ttl: Optional[float] = None) -> str:
        self.logger.info(f"Processing document from URL: {url}")
        try:
            resp = httpx.get(url)
            resp.raise_for_status()

            # Use io.BytesIO (not httpx.BytesIO)
            file_obj = io.BytesIO(resp.content)

            # Upload file using `file=` (not `path=`)
            uploaded_file = self.file_manager.upload_file(file_obj, mime_type="application/pdf")

            if use_cache:
                cache = self.caching_manager.create_cache(
                    model_name=self.model_name,
                    contents=[uploaded_file],
                    system_instruction="You are processing documents efficiently."
                )
                if cache_ttl:
                    self.caching_manager.update_cache_ttl(cache.name, hours=cache_ttl)
                response = self.caching_manager.generate_with_cache(self.model_name, cache.name, self.prompt)
            else:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[uploaded_file, self.prompt]
                )

            return response.text
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error while fetching URL {url}: {e}")
            return ""
        except Exception as e:
            self.logger.error(f"Error processing URL {url}: {e}")
            return ""

    def process_multiple_files(self, file_paths: List[Union[str, Path]], use_cache: bool = False, cache_ttl: Optional[float] = None) -> str:
        try:
            uploaded_refs = []
            for fp in file_paths:
                path_obj = Path(fp)
                mime_type = "application/pdf" if path_obj.suffix.lower() == ".pdf" else "text/plain"
                uploaded_file = self.file_manager.upload_file(path_obj, mime_type=mime_type)
                uploaded_refs.append(uploaded_file)

            contents = uploaded_refs + [self.prompt]

            if use_cache:
                cache = self.caching_manager.create_cache(
                    model_name=self.model_name,
                    contents=uploaded_refs,
                    system_instruction="You are processing documents efficiently."
                )
                if cache_ttl:
                    self.caching_manager.update_cache_ttl(cache.name, hours=cache_ttl)
                response = self.caching_manager.generate_with_cache(self.model_name, cache.name, self.prompt)
            else:
                response = self.client.models.generate_content(model=self.model_name, contents=contents)

            return response.text
        except Exception as e:
            self.logger.error(f"Error processing multiple files: {e}")
            return ""

    def process_folder(self, folder_path: Path, output_dir: Optional[Path] = None, out_ext: str = "md", use_cache: bool = False, cache_ttl: Optional[float] = None):
        if not folder_path.exists() or not folder_path.is_dir():
            self.logger.error(f"Folder does not exist: {folder_path}")
            return

        output_dir = output_dir or folder_path
        output_dir.mkdir(parents=True, exist_ok=True)
        files = [f for f in folder_path.iterdir() if f.is_file()]

        for f in tqdm(files, desc=f"Processing folder {folder_path}"):
            self.logger.info(f"Processing file: {f.name}")
            text = self.process_file(f, use_cache=use_cache, cache_ttl=cache_ttl)
            if text:
                out_file = output_dir / f"{f.stem}.{out_ext}"
                out_file.write_text(text, encoding="utf-8")
                self.logger.info(f"Saved to {out_file}")
            else:
                self.logger.warning(f"No output for {f.name}")

    def list_caches(self):
        """
        Lists all available caches.
        """
        try:
            caches = self.caching_manager.list_caches()
            return caches
        except Exception as e:
            self.logger.error(f"Failed to list caches: {e}")
            return []

    def delete_cache(self, cache_name: str):
        """
        Deletes a specific cache by its name.
        """
        try:
            self.caching_manager.delete_cache(cache_name)
            self.logger.info(f"Cache {cache_name} deleted successfully.")
        except Exception as e:
            self.logger.error(f"Failed to delete cache {cache_name}: {e}")
