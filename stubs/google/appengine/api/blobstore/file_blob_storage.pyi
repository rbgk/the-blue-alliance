from google.appengine.api.blobstore import blob_storage

class FileBlobStorage(blob_storage.BlobStorage):
    def __init__(self, storage_directory, app_id) -> None: ...
    def StoreBlob(self, blob_key, blob_stream) -> None: ...
    def OpenBlob(self, blob_key): ...
    def DeleteBlob(self, blob_key) -> None: ...