import logging
import base64
import asyncio
import os
from google.cloud import storage
from google.oauth2 import service_account
import io

from dotenv import load_dotenv
load_dotenv()

from .base_redis_cache import BaseRedisCache, with_cache
from ..enums.GoogleEnum import Bucket

class ClientGoogleCloud:
    def __init__(self):
        self._cache = None
        self._bucket = None
        self._client = self._setup_client()

    def _setup_client(self):
        credentials_info = {
            "type": "service_account",
            "project_id": os.getenv("GCP_PROJECT_ID"),
            "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
            "private_key": os.getenv("GCP_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("GCP_CLIENT_EMAIL"),
            "client_id": os.getenv("GCP_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("GCP_CERT_URL")
        }

        client = storage.Client.from_service_account_info(credentials_info)
        self._bucket = client.bucket(Bucket.BUCKET)
        return client

    def _get_cache(self) -> BaseRedisCache:
        if not self._cache:
            self._cache = BaseRedisCache()
            self._cache.initialize()
        return self._cache

    def upload_image(self, image_data, path, mime_type='image/png'):
        try:
            blob = self._bucket.blob(path)
            blob.upload_from_string(image_data, content_type=mime_type)

            cache = self._get_cache()
            cache.set(path, image_data)

            return path
        except Exception as e:
            logging.error(f"Error uploading image {path}: {e}", exc_info=True)
            raise

    def update_file(self, file_data, path, mime_type='image/png'):
        try:
            blob = self._bucket.blob(path)
            blob.upload_from_string(file_data, content_type=mime_type)

            cache = self._get_cache()
            cache.set(path, file_data)

            return path
        except Exception as e:
            logging.error(f"Error updating file {path}: {e}", exc_info=True)
            raise

    def remove_file(self, path) -> bool:
        try:
            blob = self._bucket.blob(path)
            blob.delete()
            return True
        except Exception as e:
            logging.error(f"Error removing file {path}: {e}")
            return False

    def remove_folder_by_name(self, folder_name: str) -> bool:
        try:
            blobs = self._client.list_blobs(self._bucket, prefix=folder_name + "/")
            for blob in blobs:
                blob.delete()
            return True
        except Exception as e:
            logging.error(f"Error removing folder {folder_name}: {e}", exc_info=True)
            return False

    def create_folder(self, folder_name, parent_folder_id=None):
        try:
            path = f"{folder_name.strip('/')}/"
            blob = self._bucket.blob(path)
            blob.upload_from_string(b"")
            return path
        except Exception as e:
            logging.error(f"Error creating folder {folder_name}: {e}")
            return False

    def list_folders(self, parent_folder_id=None):
        try:
            prefix = f"{parent_folder_id.strip('/')}/" if parent_folder_id else ''
            iterator = self._client.list_blobs(self._bucket, prefix=prefix, delimiter="/")
            return [prefix.strip("/") for prefix in iterator.prefixes]
        except Exception as e:
            logging.error(f"Error listing folders: {e}")
            return False

    def list_files_in_folder(self, folder_name):
        try:
            prefix = f"{folder_name.strip('/')}/"
            blobs = self._client.list_blobs(self._bucket, prefix=prefix)
            return [{"name": blob.name, "content_type": blob.content_type} for blob in blobs]
        except Exception as e:
            logging.error(f"Error listing files in folder {folder_name}: {e}")
            return False

    @with_cache(lambda self, file_id: file_id)
    def load_image(self, file_id: str):
        try:
            blob = self._bucket.blob(file_id)
            content = blob.download_as_bytes()
            if not content:
                raise ValueError("Downloaded file is empty")

            binary = base64.b64encode(content).decode("utf-8")
            return f"data:image/png;base64,{binary}"
        except Exception as e:
            logging.error(f"Error loading image {file_id}: {e}", exc_info=True)
            return None
