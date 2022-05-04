from typing import Any

def GenerateIndexFromHistory(query_history, all_indexes: Any | None = ..., manual_indexes: Any | None = ...): ...

class EmptyIndexFileError(Exception): ...

class IndexYamlUpdater:
    index_yaml_is_manual: bool
    index_yaml_mtime: Any
    last_history_size: int
    root_path: Any
    def __init__(self, root_path) -> None: ...
    def UpdateIndexConfig(self) -> None: ...
    def UpdateIndexYaml(self, openfile=...) -> None: ...

class DatastoreIndexesAutoXmlUpdater:
    auto_generated: bool
    datastore_indexes_xml: Any
    datastore_indexes_xml_mtime: Any
    datastore_indexes_auto_xml_mtime: Any
    last_history_size: int
    root_path: Any
    def __init__(self, root_path) -> None: ...
    def UpdateIndexConfig(self) -> None: ...
    def UpdateDatastoreIndexesAutoXml(self, openfile=...) -> None: ...