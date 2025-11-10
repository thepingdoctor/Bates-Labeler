"""Tests for cloud storage module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from bates_labeler.cloud_storage import (
    CloudStorageManager,
    GoogleDriveProvider,
    DropboxProvider,
    GOOGLE_DRIVE_AVAILABLE,
    DROPBOX_AVAILABLE
)


@pytest.fixture
def sample_file(tmp_path):
    """Create sample file for testing."""
    file_path = tmp_path / "sample.pdf"
    file_path.write_text("Sample PDF content")
    return file_path


class TestCloudStorageManager:
    """Test CloudStorageManager class."""

    def test_initialization(self):
        """Test manager initialization."""
        manager = CloudStorageManager()
        assert manager.providers == {}

    def test_list_providers(self):
        """Test provider listing."""
        manager = CloudStorageManager()
        assert manager.list_providers() == []

        # Add mock provider
        manager.providers['test'] = Mock()
        assert 'test' in manager.list_providers()

    def test_get_provider(self):
        """Test provider retrieval."""
        manager = CloudStorageManager()

        # Non-existent provider
        assert manager.get_provider('nonexistent') is None

        # Add mock provider
        mock_provider = Mock()
        manager.providers['test'] = mock_provider
        assert manager.get_provider('test') == mock_provider

    def test_invalid_provider_type(self):
        """Test invalid provider type handling."""
        manager = CloudStorageManager()

        with pytest.raises(ValueError):
            manager.add_provider(
                name='invalid',
                provider_type='nonexistent_provider',
                credentials={}
            )


@pytest.mark.skipif(not GOOGLE_DRIVE_AVAILABLE, reason="Google Drive dependencies not installed")
class TestGoogleDriveProvider:
    """Test GoogleDriveProvider class."""

    def test_initialization(self):
        """Test provider initialization."""
        provider = GoogleDriveProvider()
        assert provider.service is None
        assert provider.connected is False

    @patch('bates_labeler.cloud_storage.build')
    @patch('bates_labeler.cloud_storage.service_account')
    def test_connect_with_credentials_file(self, mock_service_account, mock_build):
        """Test connection with credentials file."""
        provider = GoogleDriveProvider()

        mock_creds = Mock()
        mock_service_account.Credentials.from_service_account_file.return_value = mock_creds

        credentials = {'credentials_file': '/path/to/credentials.json'}
        result = provider.connect(credentials)

        assert result is True
        assert provider.connected is True
        mock_build.assert_called_once()

    def test_operations_without_connection(self):
        """Test operations fail without connection."""
        provider = GoogleDriveProvider()

        with pytest.raises(RuntimeError):
            provider.upload_file('/path/to/file.pdf', 'remote.pdf')

        with pytest.raises(RuntimeError):
            provider.download_file('file_id', '/path/to/output.pdf')

        with pytest.raises(RuntimeError):
            provider.list_files()

        with pytest.raises(RuntimeError):
            provider.delete_file('file_id')

    @patch('bates_labeler.cloud_storage.build')
    @patch('bates_labeler.cloud_storage.service_account')
    def test_upload_file(self, mock_service_account, mock_build, sample_file):
        """Test file upload."""
        provider = GoogleDriveProvider()
        provider.connected = True

        mock_service = Mock()
        mock_service.files().create().execute.return_value = {'id': 'file123'}
        provider.service = mock_service

        file_id = provider.upload_file(sample_file, 'uploaded.pdf')

        assert file_id == 'file123'

    @patch('bates_labeler.cloud_storage.build')
    @patch('bates_labeler.cloud_storage.service_account')
    def test_list_files(self, mock_service_account, mock_build):
        """Test file listing."""
        provider = GoogleDriveProvider()
        provider.connected = True

        mock_service = Mock()
        mock_service.files().list().execute.return_value = {
            'files': [
                {'id': '1', 'name': 'file1.pdf'},
                {'id': '2', 'name': 'file2.pdf'}
            ]
        }
        provider.service = mock_service

        files = provider.list_files()

        assert len(files) == 2
        assert files[0]['name'] == 'file1.pdf'


@pytest.mark.skipif(not DROPBOX_AVAILABLE, reason="Dropbox not installed")
class TestDropboxProvider:
    """Test DropboxProvider class."""

    def test_initialization(self):
        """Test provider initialization."""
        provider = DropboxProvider()
        assert provider.client is None
        assert provider.connected is False

    @patch('bates_labeler.cloud_storage.dropbox.Dropbox')
    def test_connect(self, mock_dropbox):
        """Test connection with access token."""
        provider = DropboxProvider()

        mock_client = Mock()
        mock_client.users_get_current_account.return_value = {}
        mock_dropbox.return_value = mock_client

        credentials = {'access_token': 'test_token'}
        result = provider.connect(credentials)

        assert result is True
        assert provider.connected is True

    def test_operations_without_connection(self):
        """Test operations fail without connection."""
        provider = DropboxProvider()

        with pytest.raises(RuntimeError):
            provider.upload_file('/path/to/file.pdf', '/remote.pdf')

        with pytest.raises(RuntimeError):
            provider.download_file('/remote.pdf', '/path/to/output.pdf')

        with pytest.raises(RuntimeError):
            provider.list_files()

        with pytest.raises(RuntimeError):
            provider.delete_file('/remote.pdf')

    @patch('bates_labeler.cloud_storage.dropbox.Dropbox')
    def test_upload_file(self, mock_dropbox, sample_file):
        """Test file upload."""
        provider = DropboxProvider()
        provider.connected = True

        mock_client = Mock()
        mock_client.files_upload.return_value = Mock()
        provider.client = mock_client

        remote_path = provider.upload_file(sample_file, 'uploaded.pdf')

        assert remote_path == '/uploaded.pdf'
        mock_client.files_upload.assert_called_once()

    @patch('bates_labeler.cloud_storage.dropbox.Dropbox')
    def test_download_file(self, mock_dropbox, tmp_path):
        """Test file download."""
        provider = DropboxProvider()
        provider.connected = True

        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = b'Downloaded content'
        mock_client.files_download.return_value = (Mock(), mock_response)
        provider.client = mock_client

        output_path = tmp_path / "downloaded.pdf"
        result = provider.download_file('/remote.pdf', output_path)

        assert result == output_path
        assert output_path.exists()

    @patch('bates_labeler.cloud_storage.dropbox.Dropbox')
    @patch('bates_labeler.cloud_storage.dropbox.files')
    def test_list_files(self, mock_files, mock_dropbox):
        """Test file listing."""
        provider = DropboxProvider()
        provider.connected = True

        mock_client = Mock()
        mock_result = Mock()

        # Create mock file entries
        mock_file1 = Mock(spec=mock_files.FileMetadata)
        mock_file1.name = 'file1.pdf'
        mock_file1.path_display = '/file1.pdf'
        mock_file1.size = 1024
        mock_file1.client_modified = Mock()
        mock_file1.client_modified.isoformat.return_value = '2025-01-01T00:00:00'

        mock_result.entries = [mock_file1]
        mock_client.files_list_folder.return_value = mock_result
        provider.client = mock_client

        files = provider.list_files()

        assert len(files) == 1
        assert files[0]['name'] == 'file1.pdf'

    @patch('bates_labeler.cloud_storage.dropbox.Dropbox')
    def test_delete_file(self, mock_dropbox):
        """Test file deletion."""
        provider = DropboxProvider()
        provider.connected = True

        mock_client = Mock()
        provider.client = mock_client

        result = provider.delete_file('/remote.pdf')

        assert result is True
        mock_client.files_delete_v2.assert_called_once_with('/remote.pdf')


class TestCloudStorageIntegration:
    """Test cloud storage integration scenarios."""

    @patch('bates_labeler.cloud_storage.GoogleDriveProvider')
    def test_add_google_drive_provider(self, mock_provider_class):
        """Test adding Google Drive provider."""
        manager = CloudStorageManager()

        mock_provider = Mock()
        mock_provider.connect.return_value = True
        mock_provider_class.return_value = mock_provider

        result = manager.add_provider(
            name='my_drive',
            provider_type='google_drive',
            credentials={'credentials_file': '/path/to/creds.json'}
        )

        assert result is True
        assert 'my_drive' in manager.providers

    @patch('bates_labeler.cloud_storage.DropboxProvider')
    def test_add_dropbox_provider(self, mock_provider_class):
        """Test adding Dropbox provider."""
        manager = CloudStorageManager()

        mock_provider = Mock()
        mock_provider.connect.return_value = True
        mock_provider_class.return_value = mock_provider

        result = manager.add_provider(
            name='my_dropbox',
            provider_type='dropbox',
            credentials={'access_token': 'test_token'}
        )

        assert result is True
        assert 'my_dropbox' in manager.providers

    def test_multiple_providers(self):
        """Test managing multiple providers."""
        manager = CloudStorageManager()

        # Add mock providers
        manager.providers['drive'] = Mock()
        manager.providers['dropbox'] = Mock()

        providers = manager.list_providers()
        assert len(providers) == 2
        assert 'drive' in providers
        assert 'dropbox' in providers
