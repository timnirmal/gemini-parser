import logging
from google import genai
from pathlib import Path
from typing import Union, IO

class FileManager:
    """
    Handles file uploads, listings, retrieval, and deletion via Gemini's File API.
    """

    def __init__(self, client: genai.Client):
        """
        :param client: An instantiated genai.Client with an API key configured.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = client

    def upload_file(self, file_or_path: Union[str, Path, IO[bytes]], mime_type: str = "application/pdf"):
        """
        Uploads a file or file-like object to Gemini via the File API.
        """
        config = {"mime_type": mime_type}

        if isinstance(file_or_path, (str, Path)):
            with open(file_or_path, "rb") as f:
                uploaded_file = self.client.files.upload(file=f, config=config)
        else:
            uploaded_file = self.client.files.upload(file=file_or_path, config=config)

        self.logger.info(f"Uploaded file: {uploaded_file.name}")
        return uploaded_file

    def list_files(self):
        """
        Lists all files currently stored via the Gemini File API.
        :return: A list of File objects.
        """
        files = list(self.client.files.list())
        for f in files:
            self.logger.info(f"Found file: {f.name}")
        return files

    def get_file(self, file_name: str):
        """
        Retrieves metadata for a given file name or URI.
        :param file_name: The file name or URI.
        :return: The File object with metadata or None if not found.
        """
        try:
            file_info = self.client.files.get(file_name)
            self.logger.info(f"Metadata for {file_name}: {file_info.model_dump_json(indent=4)}")
            return file_info
        except Exception as e:
            self.logger.error(f"Error retrieving file {file_name}: {e}")
            return None

    def delete_file(self, file_name: str):
        """
        Deletes a file from Gemini by its name/URI.
        :param file_name: The file name or URI in Gemini.
        """
        try:
            self.client.files.delete(file_name)
            self.logger.info(f"Deleted file: {file_name}")
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_name}: {e}")
