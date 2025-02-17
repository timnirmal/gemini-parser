from pathlib import Path
from typing import Dict

def get_mime_type(file_path: Path, allowed_extensions: Dict[str, str]) -> str:
    """
    Returns the MIME type based on the file extension.
    Defaults to 'application/octet-stream' if unknown.
    """
    return allowed_extensions.get(file_path.suffix.lower(), 'application/octet-stream')
