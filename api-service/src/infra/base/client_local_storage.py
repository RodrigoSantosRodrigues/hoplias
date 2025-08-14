import logging
import base64
import asyncio
import os
from pathlib import Path

from .base_redis_cache import BaseRedisCache, with_cache
from ...helpers.mappers import Bucket

class ClientLocalStorage:
    def __init__(self, config):
        self.config = config
        self._cache = None

        self._root_dir = Path("./local_storage").resolve()
        self._root_dir.mkdir(parents=True, exist_ok=True)

    async def _get_cache(self) -> BaseRedisCache:
        if not self._cache:
            self._cache = BaseRedisCache(self.config)
            await self._cache.initialize()
        return self._cache

    async def upload_image(self, image_data, path, mime_type='image/png') -> str:
        try:
            file_path = self._root_dir / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logging.error(f"Uploading image to {file_path}")
            with open(file_path, 'wb') as f:
                f.write(image_data)

            cache = await self._get_cache()
            await cache.set(path, image_data)

            return str(file_path)
        except Exception as e:
            logging.error(f"Error uploading image {path}: {e}", exc_info=True)
            raise

    async def update_file(self, file_data, file_id, mime_type='image/png'):
        try:
            return await self.upload_image(file_data, file_id, mime_type)
        except Exception as e:
            logging.error(f"Error updating file {file_id}: {e}", exc_info=True)
            raise

    async def remove_file(self, file_id) -> bool:
        try:
            file_path = self._root_dir / file_id
            file_path.unlink(missing_ok=True)
            return True
        except Exception as e:
            logging.error(f"Error removing file {file_id}: {e}", exc_info=True)
            return False

    async def create_folder(self, folder_name, parent_folder_id=None):
        try:
            folder_path = self._root_dir / (parent_folder_id or '') / folder_name
            folder_path.mkdir(parents=True, exist_ok=True)
            return str(folder_path.relative_to(self._root_dir)) + '/'
        except Exception as e:
            logging.error(f"Error creating folder {folder_name}: {e}", exc_info=True)
            raise

    async def remove_folder_by_name(self, parent_folder_name: str, folder_name: str) -> bool:
        try:
            folder_path = self._root_dir / Bucket.BUCKET / parent_folder_name / folder_name
            if folder_path.exists():
                for f in folder_path.rglob("*"):
                    if f.is_file():
                        f.unlink()
                folder_path.rmdir()
            return True
        except Exception as e:
            logging.error(f"Error removing folder {folder_path}: {e}", exc_info=True)
            return False

    async def list_folders(self, parent_folder_id=None):
        try:
            base_path = self._root_dir / (parent_folder_id or '')
            return [
                {'name': f.name, 'id': str(f.relative_to(self._root_dir))}
                for f in base_path.iterdir() if f.is_dir()
            ]
        except Exception as e:
            logging.error(f"Error listing folders: {e}", exc_info=True)
            return []

    async def list_files_in_folder(self, folder_id):
        try:
            folder_path = self._root_dir / folder_id
            return [
                {
                    'id': str(f.relative_to(self._root_dir)),
                    'name': f.name,
                    'mimeType': 'image/png' if f.suffix in ['.png', '.jpg', '.jpeg'] else 'application/octet-stream'
                }
                for f in folder_path.glob('*') if f.is_file()
            ]
        except Exception as e:
            logging.error(f"Error listing files: {e}", exc_info=True)
            return []

    @with_cache(lambda self, file_id: file_id)
    async def load_image(self, file_id: str):
        logging.error(f"Loading image from local storage: {file_id}")
        try:
            file_path = self._root_dir / file_id
            with open(file_path, 'rb') as f:
                image_data = f.read()

            binary = base64.b64encode(image_data).decode('utf-8')
            return f"data:'image/png';base64,{binary}"

        except Exception as e:
            logging.error(f"Error loading image: {file_id} - {e}", exc_info=True)
            return None

    @with_cache(lambda self, file_id: file_id)
    async def load_image_(self, file_id: str):
        try:
            file_path = self._root_dir / file_id
            with open(file_path, 'rb') as f:
                image_data = f.read()

            binary = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/png;base64,{binary}"

        except Exception as e:
            logging.error(f"Error loading image: {file_id} - {e}", exc_info=True)
            return None
