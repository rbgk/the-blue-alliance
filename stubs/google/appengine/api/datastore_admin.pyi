from google.appengine.api import api_base_pb2 as api_base_pb2, apiproxy_stub_map as apiproxy_stub_map, datastore as datastore, datastore_types as datastore_types
from google.appengine.datastore import datastore_pb as datastore_pb
from google.appengine.runtime import apiproxy_errors as apiproxy_errors
from typing import Any

def GetIndices(_app: Any | None = ...): ...
def CreateIndex(index): ...
def UpdateIndex(index) -> None: ...
def DeleteIndex(index) -> None: ...