"""
Comprehensive Test Suite for Cloud Storage Integration (v2.2.0 Feature #4)

Tests cloud storage integration functionality including:
- Google Drive integration
- Dropbox integration
- File upload/download
- File listing and filtering
- Provider management
- Error handling

Note: These tests use mocking to avoid requiring actual cloud credentials.
Real integration tests should be run separately with valid credentials.
"""

import io
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from bates_labeler.cloud_storage import (
    CloudStorageProvider,
    GoogleDriveProvider,
    DropboxProvider,
    CloudStorageManager,
    GOOGLE_DRIVE_AVAILABLE,
    DROPBOX_AVAILABLE,
    S3_AVAILABLE
)


class TestCloudStorageProvider:
    """Test abstract CloudStorageProvider class."""

    def test_abstract_methods(self):
        """Test that CloudStorageProvider is abstract."""
        # Can't instantiate abstract class directly
        with pytest.raises(TypeError):
            CloudStorageProvider()


@pytest.mark.skipif(not GOOGLE_DRIVE_AVAILABLE, reason="Google Drive dependencies not installed")
class TestGoogleDriveProvider:
    """Test Google Drive integration."""

    @pytest.fixture
    def mock_service(self):
        """Create mock Google Drive service."""
        service = MagicMock()
        return service

    @pytest.fixture
    def provider(self, mock_service):
        """Create GoogleDriveProvider with mocked service."""
        provider = GoogleDriveProvider()
        provider.service = mock_service
        provider.connected = True
        return provider

    def test_provider_initialization(self):
        """Test GoogleDriveProvider initialization."""
        provider = GoogleDriveProvider()
        assert provider.service is None
        assert provider.connected is False

    def test_connect_with_credentials_file(self):
        """Test connecting with credentials file."""
        provider = GoogleDriveProvider()

        with patch('bates_labeler.cloud_storage.service_account') as mock_sa:
            with patch('bates_labeler.cloud_storage.build') as mock_build:
                mock_creds = Mock()
                mock_sa.Credentials.from_service_account_file.return_value = mock_creds
                mock_build.return_value = MagicMock()

                success = provider.connect({
                    'credentials_file': '/path/to/creds.json'
                })

                assert success
                assert provider.connected
                mock_sa.Credentials.from_service_account_file.assert_called_once()
                mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds)

    def test_upload_file(self, provider, mock_service):
        """Test uploading file to Google Drive."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdf') as tmp:
            tmp.write("test content")
            tmp_path = tmp.name

        try:
            # Mock the upload response
            mock_service.files().create().execute.return_value = {'id': 'file123'}

            file_id = provider.upload_file(tmp_path, "test.pdf")

            assert file_id == 'file123'
            mock_service.files().create.assert_called_once()
        finally:
            Path(tmp_path).unlink()

    def test_download_file(self, provider, mock_service):
        """Test downloading file from Google Drive."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Mock the download response
            mock_request = MagicMock()
            mock_service.files().get_media.return_value = mock_request

            with patch('bates_labeler.cloud_storage.MediaIoBaseDownload') as mock_download:
                mock_downloader = MagicMock()
                mock_downloader.next_chunk.return_value = (Mock(progress=lambda: 1.0), True)
                mock_download.return_value = mock_downloader

                result = provider.download_file('file123', tmp_path)

                assert result == Path(tmp_path)
                mock_service.files().get_media.assert_called_once_with(fileId='file123')
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_list_files(self, provider, mock_service):
        """Test listing files in Google Drive."""
        # Mock the list response
        mock_service.files().list().execute.return_value = {
            'files': [
                {'id': 'file1', 'name': 'doc1.pdf', 'mimeType': 'application/pdf'},
                {'id': 'file2', 'name': 'doc2.pdf', 'mimeType': 'application/pdf'}
            ]
        }

        files = provider.list_files()

        assert len(files) == 2
        assert files[0]['name'] == 'doc1.pdf'
        assert files[1]['id'] == 'file2'

    def test_list_files_with_pattern(self, provider, mock_service):
        """Test listing files with pattern filter."""
        mock_service.files().list().execute.return_value = {
            'files': [{'id': 'file1', 'name': 'test.pdf'}]
        }

        files = provider.list_files(pattern="test")

        # Verify query was constructed correctly
        call_kwargs = mock_service.files().list.call_args[1]
        assert 'test' in call_kwargs.get('q', '')

    def test_delete_file(self, provider, mock_service):
        """Test deleting file from Google Drive."""
        success = provider.delete_file('file123')

        assert success
        mock_service.files().delete.assert_called_once_with(fileId='file123')

    def test_not_connected_error(self):
        """Test errors when not connected."""
        provider = GoogleDriveProvider()
        provider.connected = False

        with pytest.raises(RuntimeError, match="Not connected"):
            provider.upload_file("/path/to/file.pdf", "test.pdf")

        with pytest.raises(RuntimeError, match="Not connected"):
            provider.download_file("file123", "/path/to/output.pdf")

        with pytest.raises(RuntimeError, match="Not connected"):
            provider.list_files()

        with pytest.raises(RuntimeError, match="Not connected"):
            provider.delete_file("file123")


@pytest.mark.skipif(not DROPBOX_AVAILABLE, reason="Dropbox dependencies not installed")
class TestDropboxProvider:
    """Test Dropbox integration."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Dropbox client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def provider(self, mock_client):
        """Create DropboxProvider with mocked client."""
        provider = DropboxProvider()
        provider.client = mock_client
        provider.connected = True
        return provider

    def test_provider_initialization(self):
        """Test DropboxProvider initialization."""
        provider = DropboxProvider()
        assert provider.client is None
        assert provider.connected is False

    def test_connect(self):
        """Test connecting to Dropbox."""
        provider = DropboxProvider()

        with patch('bates_labeler.cloud_storage.dropbox.Dropbox') as mock_dropbox:
            mock_client = MagicMock()
            mock_dropbox.return_value = mock_client

            success = provider.connect({'access_token': 'test_token'})

            assert success
            assert provider.connected
            mock_dropbox.assert_called_once_with('test_token')
            mock_client.users_get_current_account.assert_called_once()

    def test_upload_file(self, provider, mock_client):
        """Test uploading file to Dropbox."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdf') as tmp:
            tmp.write("test content")
            tmp_path = tmp.name

        try:
            remote_path = provider.upload_file(tmp_path, "test.pdf")

            assert remote_path == "/test.pdf"
            mock_client.files_upload.assert_called_once()
        finally:
            Path(tmp_path).unlink()

    def test_upload_file_adds_leading_slash(self, provider, mock_client):
        """Test that upload adds leading slash to path."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test")
            tmp_path = tmp.name

        try:
            # Path without leading slash
            remote_path = provider.upload_file(tmp_path, "folder/test.pdf")

            # Should add leading slash
            assert remote_path == "/folder/test.pdf"
        finally:
            Path(tmp_path).unlink()

    def test_download_file(self, provider, mock_client):
        """Test downloading file from Dropbox."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Mock the download response
            mock_response = MagicMock()
            mock_response.content = b"downloaded content"
            mock_client.files_download.return_value = (Mock(), mock_response)

            result = provider.download_file("/test.pdf", tmp_path)

            assert result == Path(tmp_path)
            assert Path(tmp_path).read_bytes() == b"downloaded content"
            mock_client.files_download.assert_called_once_with("/test.pdf")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_list_files(self, provider, mock_client):
        """Test listing files in Dropbox."""
        # Mock file metadata
        with patch('bates_labeler.cloud_storage.dropbox.files.FileMetadata') as mock_file_meta:
            mock_file1 = MagicMock()
            mock_file1.name = "doc1.pdf"
            mock_file1.path_display = "/docs/doc1.pdf"
            mock_file1.size = 1024
            mock_file1.client_modified.isoformat.return_value = "2024-01-01T00:00:00"

            mock_result = MagicMock()
            mock_result.entries = [mock_file1]
            mock_client.files_list_folder.return_value = mock_result

            files = provider.list_files("")

            assert len(files) >= 1
            assert files[0]['name'] == "doc1.pdf"
            assert files[0]['size'] == 1024

    def test_delete_file(self, provider, mock_client):
        """Test deleting file from Dropbox."""
        success = provider.delete_file("/test.pdf")

        assert success
        mock_client.files_delete_v2.assert_called_once_with("/test.pdf")


class TestCloudStorageManager:
    """Test CloudStorageManager multi-provider functionality."""

    def test_manager_initialization(self):
        """Test CloudStorageManager initialization."""
        manager = CloudStorageManager()
        assert len(manager.providers) == 0

    @pytest.mark.skipif(not GOOGLE_DRIVE_AVAILABLE, reason="Google Drive not available")
    def test_add_google_drive_provider(self):
        """Test adding Google Drive provider."""
        manager = CloudStorageManager()

        with patch('bates_labeler.cloud_storage.GoogleDriveProvider') as mock_provider_class:
            mock_provider = MagicMock()
            mock_provider.connect.return_value = True
            mock_provider_class.return_value = mock_provider

            success = manager.add_provider(
                name='my_drive',
                provider_type='google_drive',
                credentials={'credentials_file': '/path/to/creds.json'}
            )

            assert success
            assert 'my_drive' in manager.providers
            mock_provider.connect.assert_called_once()

    @pytest.mark.skipif(not DROPBOX_AVAILABLE, reason="Dropbox not available")
    def test_add_dropbox_provider(self):
        """Test adding Dropbox provider."""
        manager = CloudStorageManager()

        with patch('bates_labeler.cloud_storage.DropboxProvider') as mock_provider_class:
            mock_provider = MagicMock()
            mock_provider.connect.return_value = True
            mock_provider_class.return_value = mock_provider

            success = manager.add_provider(
                name='my_dropbox',
                provider_type='dropbox',
                credentials={'access_token': 'test_token'}
            )

            assert success
            assert 'my_dropbox' in manager.providers

    def test_add_unknown_provider_type(self):
        """Test error when adding unknown provider type."""
        manager = CloudStorageManager()

        with pytest.raises(ValueError, match="Unknown provider type"):
            manager.add_provider(
                name='test',
                provider_type='unknown_provider',
                credentials={}
            )

    def test_get_provider(self):
        """Test getting provider by name."""
        manager = CloudStorageManager()

        with patch('bates_labeler.cloud_storage.GoogleDriveProvider') as mock_provider_class:
            mock_provider = MagicMock()
            mock_provider.connect.return_value = True
            mock_provider_class.return_value = mock_provider

            manager.add_provider('test_drive', 'google_drive', {})

            provider = manager.get_provider('test_drive')
            assert provider is not None

            nonexistent = manager.get_provider('nonexistent')
            assert nonexistent is None

    def test_list_providers(self):
        """Test listing all providers."""
        manager = CloudStorageManager()

        with patch('bates_labeler.cloud_storage.GoogleDriveProvider') as mock_gd:
            with patch('bates_labeler.cloud_storage.DropboxProvider') as mock_db:
                mock_gd.return_value.connect.return_value = True
                mock_db.return_value.connect.return_value = True

                manager.add_provider('drive1', 'google_drive', {})
                manager.add_provider('dropbox1', 'dropbox', {})

                providers = manager.list_providers()
                assert len(providers) == 2
                assert 'drive1' in providers
                assert 'dropbox1' in providers


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.skipif(not GOOGLE_DRIVE_AVAILABLE, reason="Google Drive not available")
    def test_connection_failure(self):
        """Test handling of connection failures."""
        provider = GoogleDriveProvider()

        with patch('bates_labeler.cloud_storage.service_account') as mock_sa:
            mock_sa.Credentials.from_service_account_file.side_effect = Exception("Connection failed")

            success = provider.connect({'credentials_file': '/invalid/path.json'})

            assert not success
            assert not provider.connected

    @pytest.mark.skipif(not DROPBOX_AVAILABLE, reason="Dropbox not available")
    def test_dropbox_missing_access_token(self):
        """Test error when access token missing."""
        provider = DropboxProvider()

        success = provider.connect({})  # No access_token

        assert not success

    def test_manager_add_provider_connection_failure(self):
        """Test manager handling of provider connection failure."""
        manager = CloudStorageManager()

        with patch('bates_labeler.cloud_storage.GoogleDriveProvider') as mock_provider_class:
            mock_provider = MagicMock()
            mock_provider.connect.return_value = False  # Connection fails
            mock_provider_class.return_value = mock_provider

            success = manager.add_provider('test', 'google_drive', {})

            assert not success
            assert 'test' not in manager.providers


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
