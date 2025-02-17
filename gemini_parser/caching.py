import logging
from google import genai
from google.genai import types
import datetime

class CachingManager:
    """
    Handles context caching with Gemini's Caches API.
    """

    def __init__(self, client: genai.Client):
        """
        :param client: An instantiated genai.Client with the relevant API key.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = client

    def create_cache(self, model_name: str, contents, system_instruction: str = ""):
        """
        Creates a new cached content object.
        :param model_name: e.g. 'gemini-1.5-flash'
        :param contents: List of content (files, strings) to be cached.
        :param system_instruction: Optional system instruction to store in the cache.
        :return: The created cached content object.
        """
        config = types.CreateCachedContentConfig(
            system_instruction=system_instruction,
            contents=contents
        )
        cache = self.client.caches.create(
            model=model_name,
            config=config
        )
        self.logger.info(f"Created cache: {cache.name}")
        return cache

    def generate_with_cache(self, model_name: str, cached_content_name: str, prompt: str):
        """
        Generates new text from existing cached content.
        :param model_name: The model to use, e.g. 'gemini-1.5-flash'
        :param cached_content_name: The name (ID) of the cached content.
        :param prompt: The text prompt to pass.
        :return: Generated text from Gemini.
        """
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(cached_content=cached_content_name)
        )
        return response

    def list_caches(self):
        """
        Lists cached content metadata. The actual contents are not retrievable.
        :return: A list of CachedContent objects.
        """
        caches = list(self.client.caches.list())
        for c in caches:
            self.logger.info(f"Cache found: {c.name}")
        return caches

    def update_cache_ttl(self, cache_name: str, hours: float = 2.0):
        """
        Updates the TTL of a cache to a new time in hours.
        :param cache_name: The name of the cache to update.
        :param hours: Number of hours from now until expiration.
        """
        ttl_seconds = int(hours * 3600)
        config = types.UpdateCachedContentConfig(ttl=f"{ttl_seconds}s")
        self.client.caches.update(
            name=cache_name,
            config=config
        )
        self.logger.info(f"Updated cache {cache_name} TTL to {hours} hours.")

    def delete_cache(self, cache_name: str):
        """
        Deletes a cache by name.
        """
        try:
            self.client.caches.delete(name=cache_name)
            self.logger.info(f"Deleted cache {cache_name}")
        except Exception as e:
            self.logger.error(f"Failed to delete cache {cache_name}: {e}")
