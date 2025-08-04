import logging
import base64
import asyncio
import os
from google.cloud import storage
from google.oauth2 import service_account
import io

from .base_redis_cache import BaseRedisCache, with_cache
from ...helpers.mappers import Bucket

class ClientGoogleCloudStorage:
    def __init__(self, config, user_credentials=None):
        self.config = config
        self.user_credentials = user_credentials
        self._cache = None
        self._client = None
        self._bucket = None
        self._setup_client()

    def _setup_client(self):
        credentials_info = {
            "type": "service_account",
            "project_id": self.config.GCP_PROJECT_ID,
            "private_key_id": self.config.GCP_PRIVATE_KEY_ID,
            "private_key": self.config.GCP_PRIVATE_KEY.replace('\\n', '\n'),
            "client_email": self.config.GCP_CLIENT_EMAIL,
            "client_id": self.config.GCP_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": self.config.GCP_CERT_URL
        }

        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        self._client = storage.Client(credentials=credentials, project=self.config.GCP_PROJECT_ID)
        self._bucket = self._client.bucket(Bucket.BUCKET)

    async def _get_cache(self) -> BaseRedisCache:
        if not self._cache:
            self._cache = BaseRedisCache(self.config)
            await self._cache.initialize()
        return self._cache

    async def upload_image(self, image_data, path, mime_type='image/png') -> str:
        try:
            blob = self._bucket.blob(path)
            blob.upload_from_string(image_data, content_type=mime_type)

            cache = await self._get_cache()
            await cache.set(path, image_data)

            return path
        except Exception as e:
            logging.error(f"Error uploading image {path}: {e}", exc_info=True)
            raise

    async def update_file(self, file_data, file_id, mime_type='image/png'):
        try:
            blob = self._bucket.blob(file_id)
            blob.upload_from_string(file_data, content_type=mime_type)

            cache = await self._get_cache()
            await cache.set(file_id, file_data)

            return file_id
        except Exception as e:
            logging.error(f"Error updating file {file_id}: {e}", exc_info=True)
            raise

    async def remove_file(self, file_id) -> bool:
        try:
            blob = self._bucket.blob(file_id)
            blob.delete()
            return True
        except Exception as e:
            logging.error(f"Error removing file {file_id}: {e}", exc_info=True)
            return False

    async def create_folder(self, folder_name, parent_folder_id=None):
        # GCS uses object prefixes, not actual folders.
        folder_path = f"{folder_name.strip('/')}/"
        blob = self._bucket.blob(folder_path)
        blob.upload_from_string('', content_type='application/x-directory')
        return folder_path

    async def remove_folder_by_name(self, parent_folder_name: str, folder_name: str) -> bool:
        prefix = f"{parent_folder_name.strip('/')}/{folder_name.strip('/')}/"
        try:
            blobs = list(self._bucket.list_blobs(prefix=prefix))
            if not blobs:
                logging.info(f"No blobs found in folder {prefix}")
                return True
        
            loop = asyncio.get_event_loop()
            await asyncio.gather(*[
                loop.run_in_executor(None, blob.delete)  # Replaces to_thread
                for blob in blobs
            ])
            return True
        except Exception as e:
            logging.error(f"Error removing folder {prefix}: {e}", exc_info=True)
            return False

    async def list_folders(self, parent_folder_id=None):
        try:
            prefix = f"{parent_folder_id.strip('/')}/" if parent_folder_id else ''
            blobs = self._bucket.list_blobs(prefix=prefix, delimiter='/')

            folders = []
            for page in blobs.pages:
                folders += [{'name': p, 'id': p} for p in page.prefixes]

            return folders
        except Exception as e:
            logging.error(f"Error listing folders: {e}", exc_info=True)
            return []

    async def list_files_in_folder(self, folder_id):
        try:
            prefix = f"{folder_id.strip('/')}/"
            blobs = self._bucket.list_blobs(prefix=prefix)
            return [{'id': blob.name, 'name': os.path.basename(blob.name), 'mimeType': blob.content_type} for blob in blobs]
        except Exception as e:
            logging.error(f"Error listing files: {e}", exc_info=True)
            return []

    @with_cache(lambda self, file_id: file_id)
    async def load_image(self, file_id: str):
        loop = asyncio.get_running_loop()
        try:
            def _download_blob():
                blob = self._bucket.blob(file_id)
                image_data = blob.download_as_bytes()
                if not image_data:
                    raise ValueError("Downloaded file is empty")
                return image_data

            image_data = await asyncio.wait_for(loop.run_in_executor(None, _download_blob), timeout=30.0)
            binary = base64.b64encode(image_data).decode('utf-8')
            return f"data:'image/png';base64,{binary}"

        except asyncio.TimeoutError:
            logging.error(f"Timeout downloading file: {file_id}")
            raise
        except Exception as e:
            logging.error(f"Error loading image: {file_id} - {e}", exc_info=True)
            raise
    
    @with_cache(lambda self, file_id: file_id)
    async def load_image_(self, file_id: str):
        try:
            blob = self._bucket.blob(file_id)
            image_data = blob.download_as_bytes()

            if not image_data:
                raise ValueError("Downloaded file is empty")

            binary = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/png;base64,{binary}"

        except Exception as e:
            logging.error(f"Error loading image: {file_id} - {e}", exc_info=True)
            raise
