"""Cloud Storage Integration for Bates-Labeler.

This module provides cloud storage connectivity for seamless PDF processing:
- Google Drive integration
- Dropbox support
- AWS S3 integration
- OneDrive/SharePoint support
- Automatic upload/download
- File synchronization

Optional dependencies required for each provider.
"""

import io
import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


# Check for optional cloud storage dependencies
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

try:
    import dropbox
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False

try:
    import boto3
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

try:
    from onedrivesdk import OneDriveClient
    from onedrivesdk.helpers import GetAuthCodeServer
    ONEDRIVE_AVAILABLE = True
except ImportError:
    ONEDRIVE_AVAILABLE = False


class CloudStorageProvider(ABC):
    """Abstract base class for cloud storage providers.

    All cloud storage integrations should inherit from this class
    and implement the required methods.
    """

    @abstractmethod
    def connect(self, credentials: Dict[str, Any]) -> bool:
        """Connect to cloud storage provider.

        Args:
            credentials: Provider-specific credentials

        Returns:
            True if connection successful
        """
        pass

    @abstractmethod
    def upload_file(
        self,
        local_path: Union[str, Path],
        remote_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upload file to cloud storage.

        Args:
            local_path: Local file path
            remote_path: Remote file path
            metadata: Optional file metadata

        Returns:
            Remote file ID or path
        """
        pass

    @abstractmethod
    def download_file(
        self,
        remote_path: str,
        local_path: Union[str, Path]
    ) -> Path:
        """Download file from cloud storage.

        Args:
            remote_path: Remote file path or ID
            local_path: Local file path

        Returns:
            Local file path
        """
        pass

    @abstractmethod
    def list_files(
        self,
        folder_path: str = "",
        pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List files in cloud storage.

        Args:
            folder_path: Folder path to list
            pattern: Optional file pattern filter

        Returns:
            List of file metadata dictionaries
        """
        pass

    @abstractmethod
    def delete_file(self, remote_path: str) -> bool:
        """Delete file from cloud storage.

        Args:
            remote_path: Remote file path or ID

        Returns:
            True if deleted successfully
        """
        pass


class GoogleDriveProvider(CloudStorageProvider):
    """Google Drive integration provider.

    Requires google-auth and google-api-python-client packages.
    """

    def __init__(self):
        """Initialize Google Drive provider."""
        if not GOOGLE_DRIVE_AVAILABLE:
            raise ImportError(
                "Google Drive dependencies not installed. Install with: "
                "pip install google-auth google-api-python-client"
            )

        self.service = None
        self.connected = False

    def connect(self, credentials: Dict[str, Any]) -> bool:
        """Connect to Google Drive.

        Args:
            credentials: Dictionary with 'credentials_file' or credentials object

        Returns:
            True if connection successful
        """
        try:
            if 'credentials_file' in credentials:
                # Load from file
                from google.oauth2 import service_account
                creds = service_account.Credentials.from_service_account_file(
                    credentials['credentials_file'],
                    scopes=['https://www.googleapis.com/auth/drive']
                )
            else:
                # Use provided credentials
                creds = credentials.get('credentials')

            self.service = build('drive', 'v3', credentials=creds)
            self.connected = True

            logger.info("Connected to Google Drive")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Google Drive: {e}")
            return False

    def upload_file(
        self,
        local_path: Union[str, Path],
        remote_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upload file to Google Drive.

        Args:
            local_path: Local file path
            remote_path: Remote file name
            metadata: Optional file metadata

        Returns:
            File ID in Google Drive
        """
        if not self.connected:
            raise RuntimeError("Not connected to Google Drive")

        local_path = Path(local_path)

        file_metadata = {
            'name': remote_path or local_path.name
        }

        if metadata:
            file_metadata.update(metadata)

        media = MediaFileUpload(str(local_path), resumable=True)

        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        file_id = file.get('id')
        logger.info(f"Uploaded to Google Drive: {remote_path} (ID: {file_id})")

        return file_id

    def download_file(
        self,
        remote_path: str,
        local_path: Union[str, Path]
    ) -> Path:
        """Download file from Google Drive.

        Args:
            remote_path: File ID in Google Drive
            local_path: Local file path

        Returns:
            Local file path
        """
        if not self.connected:
            raise RuntimeError("Not connected to Google Drive")

        local_path = Path(local_path)

        request = self.service.files().get_media(fileId=remote_path)

        with open(local_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

        logger.info(f"Downloaded from Google Drive: {remote_path}")
        return local_path

    def list_files(
        self,
        folder_path: str = "",
        pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List files in Google Drive.

        Args:
            folder_path: Folder ID (empty for root)
            pattern: Optional file name pattern

        Returns:
            List of file metadata
        """
        if not self.connected:
            raise RuntimeError("Not connected to Google Drive")

        query = []

        if folder_path:
            query.append(f"'{folder_path}' in parents")

        if pattern:
            query.append(f"name contains '{pattern}'")

        query_str = " and ".join(query) if query else None

        results = self.service.files().list(
            q=query_str,
            fields="files(id, name, mimeType, size, createdTime)"
        ).execute()

        return results.get('files', [])

    def delete_file(self, remote_path: str) -> bool:
        """Delete file from Google Drive.

        Args:
            remote_path: File ID

        Returns:
            True if deleted successfully
        """
        if not self.connected:
            raise RuntimeError("Not connected to Google Drive")

        try:
            self.service.files().delete(fileId=remote_path).execute()
            logger.info(f"Deleted from Google Drive: {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete from Google Drive: {e}")
            return False


class DropboxProvider(CloudStorageProvider):
    """Dropbox integration provider.

    Requires dropbox package.
    """

    def __init__(self):
        """Initialize Dropbox provider."""
        if not DROPBOX_AVAILABLE:
            raise ImportError(
                "Dropbox not installed. Install with: pip install dropbox"
            )

        self.client = None
        self.connected = False

    def connect(self, credentials: Dict[str, Any]) -> bool:
        """Connect to Dropbox.

        Args:
            credentials: Dictionary with 'access_token'

        Returns:
            True if connection successful
        """
        try:
            access_token = credentials.get('access_token')
            if not access_token:
                raise ValueError("access_token required")

            self.client = dropbox.Dropbox(access_token)

            # Test connection
            self.client.users_get_current_account()

            self.connected = True
            logger.info("Connected to Dropbox")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Dropbox: {e}")
            return False

    def upload_file(
        self,
        local_path: Union[str, Path],
        remote_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upload file to Dropbox.

        Args:
            local_path: Local file path
            remote_path: Remote file path (must start with /)
            metadata: Optional file metadata (unused)

        Returns:
            Remote file path
        """
        if not self.connected:
            raise RuntimeError("Not connected to Dropbox")

        local_path = Path(local_path)

        if not remote_path.startswith('/'):
            remote_path = '/' + remote_path

        with open(local_path, 'rb') as f:
            self.client.files_upload(
                f.read(),
                remote_path,
                mode=dropbox.files.WriteMode.overwrite
            )

        logger.info(f"Uploaded to Dropbox: {remote_path}")
        return remote_path

    def download_file(
        self,
        remote_path: str,
        local_path: Union[str, Path]
    ) -> Path:
        """Download file from Dropbox.

        Args:
            remote_path: Remote file path
            local_path: Local file path

        Returns:
            Local file path
        """
        if not self.connected:
            raise RuntimeError("Not connected to Dropbox")

        local_path = Path(local_path)

        metadata, response = self.client.files_download(remote_path)

        with open(local_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"Downloaded from Dropbox: {remote_path}")
        return local_path

    def list_files(
        self,
        folder_path: str = "",
        pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List files in Dropbox.

        Args:
            folder_path: Folder path (empty for root)
            pattern: Optional file name pattern

        Returns:
            List of file metadata
        """
        if not self.connected:
            raise RuntimeError("Not connected to Dropbox")

        folder_path = folder_path or ''

        result = self.client.files_list_folder(folder_path)

        files = []
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                if pattern is None or pattern in entry.name:
                    files.append({
                        'name': entry.name,
                        'path': entry.path_display,
                        'size': entry.size,
                        'modified': entry.client_modified.isoformat()
                    })

        return files

    def delete_file(self, remote_path: str) -> bool:
        """Delete file from Dropbox.

        Args:
            remote_path: Remote file path

        Returns:
            True if deleted successfully
        """
        if not self.connected:
            raise RuntimeError("Not connected to Dropbox")

        try:
            self.client.files_delete_v2(remote_path)
            logger.info(f"Deleted from Dropbox: {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete from Dropbox: {e}")
            return False


class CloudStorageManager:
    """Multi-provider cloud storage manager.

    Provides unified interface for multiple cloud storage providers.
    """

    PROVIDERS = {
        'google_drive': GoogleDriveProvider,
        'dropbox': DropboxProvider,
    }

    def __init__(self):
        """Initialize cloud storage manager."""
        self.providers: Dict[str, CloudStorageProvider] = {}

    def add_provider(
        self,
        name: str,
        provider_type: str,
        credentials: Dict[str, Any]
    ) -> bool:
        """Add and connect a cloud storage provider.

        Args:
            name: Provider instance name
            provider_type: Provider type (google_drive, dropbox, etc.)
            credentials: Provider credentials

        Returns:
            True if connected successfully
        """
        if provider_type not in self.PROVIDERS:
            raise ValueError(f"Unknown provider type: {provider_type}")

        provider_class = self.PROVIDERS[provider_type]
        provider = provider_class()

        if provider.connect(credentials):
            self.providers[name] = provider
            return True

        return False

    def get_provider(self, name: str) -> Optional[CloudStorageProvider]:
        """Get provider by name.

        Args:
            name: Provider instance name

        Returns:
            Provider instance or None
        """
        return self.providers.get(name)

    def list_providers(self) -> List[str]:
        """List connected provider names.

        Returns:
            List of provider names
        """
        return list(self.providers.keys())
