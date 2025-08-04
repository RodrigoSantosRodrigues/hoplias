import logging
import base64
import asyncio
import os
import logging
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
import io
from .base_redis_cache import BaseRedisCache, with_cache



SCOPES = ['https://www.googleapis.com/auth/drive']

class ClientGoogleDrive():
    def __init__(self, config, user_credentials=None):
        self.config = config
        self.user_credentials = user_credentials
        self._cache = None
        
        if self.user_credentials:
            self._load_user_credentials()
        else:
            self._get_credentials()

    def _get_credentials(self):
        """Carrega credenciais diretamente de env vars"""
        credentials = service_account.Credentials.from_service_account_info({
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
        }, scopes=['https://www.googleapis.com/auth/drive'])

        self.service = build('drive', 'v3', credentials=credentials)

    def _load_user_credentials(self):
        if not self.user_credentials or not self.user_credentials.valid:
            if self.user_credentials and self.user_credentials.expired and self.user_credentials.refresh_token:
                self.user_credentials.refresh(Request())
            else:
                raise Exception("Not authenticated. Please authenticate using the OAuth flow.")
     
        self.service = build('drive', 'v3', credentials=self.user_credentials)
    
    async def _get_cache(self) -> BaseRedisCache:
        try:
            if not self._cache:
                self._cache = BaseRedisCache(self.config)
                await self._cache.initialize()
            return self._cache
        except Exception as e:
            logging.error(f"Error in _get_cache: {str(e)}", exc_info=True)
            raise

    @classmethod
    async def exchange_code_for_token(cls, authorization_response):
        """Exchange authorization code for tokens and initialize the service"""
        try:
            flow = Flow.from_client_config(
                client_config={
                    "web": {
                        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                scopes=SCOPES,
                redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
            )
           
            flow.fetch_token(authorization_response=authorization_response)
            user_credentials = flow.credentials
     
            service = build('drive', 'v3', credentials=user_credentials)
            service.files().list(pageSize=1).execute()
        
            return user_credentials.to_json()
            
        except Exception as e:
            logging.error(f"Error in token exchange: {str(e)}", exc_info=True)
            raise

    async def upload_image(self, image_data, path, mime_type='image/png') -> str:
        try:
            image_bytes = image_data
            path_parts = path.split('/')
            filename = path_parts[-1]
            folder_structure = path_parts[:-1]
            current_parent = None
            
            for folder_name in folder_structure:
                query = [
                    f"name='{folder_name}'",
                    "mimeType='application/vnd.google-apps.folder'",
                    f"'{current_parent}' in parents" if current_parent else ""
                ]
                query = " and ".join(filter(None, query))
                
                existing_folders = self.service.files().list(
                    q=query,
                    spaces='drive',
                    fields='files(id)',
                    pageSize=1
                ).execute().get('files', [])
                
                if existing_folders:
                    current_parent = existing_folders[0]['id']
                else:
                    folder_metadata = {
                        'name': folder_name,
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [current_parent] if current_parent else []
                    }
                    folder = self.service.files().create(
                        body=folder_metadata,
                        fields='id'
                    ).execute()
                    current_parent = folder.get('id')
     
            file_metadata = {
                'name': filename,
                'parents': [current_parent] if current_parent else []
            }
            
            media = MediaIoBaseUpload(
                io.BytesIO(image_bytes),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            file_id = file.get('id')
      
            cache = await self._get_cache()
            await cache.set(file_id, image_bytes)
    
            return file_id
        except Exception as e:
            logging.error(f"Error uploading image {path}: {e}", exc_info=True)
            raise

    async def update_file(self, file_data, file_id, mime_type='image/png'):
        try:
            media = MediaIoBaseUpload(
                io.BytesIO(file_data),
                mimetype=mime_type,
                resumable=True
            )
  
            updated_file = self.service.files().update(
                fileId=file_id,
                media_body=media,
                fields='id'
            ).execute()

            cache = await self._get_cache()
            await cache.set(updated_file.get('id'), file_data)
            
            return updated_file.get('id')
        
        except Exception as e:
            logging.error(
                f"Error updating file ID {file_id}: {str(e)}",
                exc_info=True
            )
            raise

    async def remove_file(self, file_id) -> bool:
        try:
            self.service.files().delete(fileId=file_id).execute()
        except Exception as e:
            logging.error(f"Error removing file {file_id}: {e}.")
            return False
        return True

    async def remove_folder_by_name(self, parent_folder_name: str, folder_name: str) -> bool:
        try:
            parent_query = [
                f"name='{parent_folder_name}'",
                "mimeType='application/vnd.google-apps.folder'",
                "trashed=false"
            ]
            parent_query = " and ".join(filter(None, parent_query))

            parent_folders = self.service.files().list(
                q=parent_query,
                spaces='drive',
                fields='files(id)',
                pageSize=1
            ).execute().get('files', [])

            if not parent_folders:
                logging.warning(f"No parent folder named '{parent_folder_name}' found.")
                return False

            parent_id = parent_folders[0]['id']
     
            child_query = [
                f"name='{folder_name}'",
                f"'{parent_id}' in parents",
                "mimeType='application/vnd.google-apps.folder'",
                "trashed=false"
            ]
            child_query = " and ".join(filter(None, child_query))

            child_folders = self.service.files().list(
                q=child_query,
                spaces='drive',
                fields='files(id)',
                pageSize=1
            ).execute().get('files', [])

            if not child_folders:
                logging.warning(f"No child folder named '{folder_name}' found under parent '{parent_folder_name}'.")
                return False

            folder_id = child_folders[0]['id']
 
            self.service.files().delete(fileId=folder_id).execute()
            return True

        except Exception as e:
            logging.error(f"Unexpected error removing folder: {e}", exc_info=True)
            return False


    async def create_folder(self, folder_name, parent_folder_id=None):
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id] if parent_folder_id else []
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
        except Exception as e:
            logging.error(f"Error creating folder google drive: {e}.")
            return False
        
    async def list_folders(self, parent_folder_id=None):
        try:
            query = "mimeType='application/vnd.google-apps.folder'"
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name)"
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
            logging.error(f"Error creating folder google drive: {e}.")
            return False
        
    async def list_files_in_folder(self, folder_id):
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents",
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType)"
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
                logging.error(f"Error listing files google drive: {e}.")
                return False

    @with_cache(lambda self, file_id: file_id)
    async def load_image(self, file_id: str):
        """Async version using thread pool for blocking operations with improved download reliability"""
        loop = asyncio.get_running_loop()
        try:
            def _download_file():
                request = self.service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                
                downloaded_bytes = 0
                while True:
                    try:
                        status, done = downloader.next_chunk()
                        if status:
                            downloaded_bytes = status.resumable_progress
                            logging.debug(f"Download progress: {downloaded_bytes} bytes")
                        if done:
                            break
                    except Exception as e:
                        logging.error(f"Download error at {downloaded_bytes} bytes: {e}")
                        raise
        
                if fh.tell() == 0:
                    raise ValueError("Downloaded file is empty")
                    
                return fh.getvalue()

            image_data = await asyncio.wait_for(
                loop.run_in_executor(None, _download_file),
                timeout=30.0
            )
            binary = base64.b64encode(image_data).decode('utf-8')
            return f"data:'image/png';base64,{binary}"
            
        except asyncio.TimeoutError:
            logging.error(f"Timeout while downloading image {file_id}")
            return None
        except Exception as e:
            logging.error(f"Error loading image {file_id}: {e}", exc_info=True)
            return None

    @with_cache(lambda self, file_id: file_id)
    async def load_image_(self, file_id: str):
        """Async version using thread pool for blocking operations with improved download reliability"""
        try:
         
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            downloaded_bytes = 0
            while True:
                try:
                    status, done = downloader.next_chunk()
                    if status:
                        downloaded_bytes = status.resumable_progress
                    if done:
                        break
                except Exception as e:
                    logging.error(f"Download error at {downloaded_bytes} bytes: {e}")
                    raise
    
            if fh.tell() == 0:
                raise ValueError("Downloaded file is empty")
                
            image_data = fh.getvalue()
            binary = base64.b64encode(image_data).decode('utf-8')
            return f"data:'image/png';base64,{binary}"

        except Exception as e:
            logging.error(f"Error loading image {file_id}: {e}", exc_info=True)
            return None
