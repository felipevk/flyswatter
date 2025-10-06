from app.core.errors import BlobError

import pytest

from app.blob.storage import upload

def test_upload_success(mockMinIO):
    assert upload("bla.txt", "bla") == "Mock.pdf"

def test_upload_bloberror(mockMinIOFailure):
    with pytest.raises(BlobError):
        upload("bla.txt", "bla")