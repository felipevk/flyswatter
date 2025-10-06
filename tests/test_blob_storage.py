import pytest

from app.blob.storage import upload
from app.core.errors import BlobError


def test_upload_success(mockMinIO):
    assert upload("bla.txt", "bla") == "Mock.pdf"


def test_upload_bloberror(mockMinIOFailure):
    with pytest.raises(BlobError):
        upload("bla.txt", "bla")
