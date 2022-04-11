import threading
from concurrent import futures
from google.appengine.api import apiproxy_rpc as apiproxy_rpc
from google.appengine.runtime import apiproxy_errors as apiproxy_errors
from typing import Any

def CreateRPC(service, stubmap: Any | None = ...): ...
def MakeSyncCall(service, call, request, response, stubmap: Any | None = ...): ...

class ListOfHooks:
    def __init__(self) -> None: ...
    def __len__(self): ...
    def Append(self, key, function, service: Any | None = ...): ...
    def Push(self, key, function, service: Any | None = ...): ...
    def Clear(self) -> None: ...
    def Call(self, service, call, request, response, rpc: Any | None = ..., error: Any | None = ...) -> None: ...

class _CancelFuture(futures.Future): ...

class WaitCanceller:
    future: Any
    def __init__(self) -> None: ...
    def cancel(self) -> None: ...

class APIProxyStubMap:
    def __init__(self, default_stub: Any | None = ...) -> None: ...
    def SetDefaultStub(self, stub) -> None: ...
    def GetPreCallHooks(self): ...
    def GetPostCallHooks(self): ...
    def ReplaceStub(self, service, stub) -> None: ...
    def RegisterStub(self, service, stub) -> None: ...
    def GetStub(self, service): ...
    def MakeSyncCall(self, service, call, request, response): ...
    def CancelApiCalls(self) -> None: ...

class UserRPC:
    class MyLocal(threading.local):
        may_interrupt_wait: bool
    callback: Any
    def __init__(self, service, deadline: Any | None = ..., callback: Any | None = ..., stubmap: Any | None = ...) -> None: ...
    @property
    def service(self): ...
    @property
    def method(self): ...
    @property
    def deadline(self): ...
    @property
    def request(self): ...
    @property
    def response(self): ...
    @property
    def state(self): ...
    @property
    def get_result_hook(self): ...
    @property
    def user_data(self): ...
    @property
    def future(self): ...
    def make_call(self, method, request, response, get_result_hook: Any | None = ..., user_data: Any | None = ...) -> None: ...
    def wait(self) -> None: ...
    def check_success(self) -> None: ...
    def get_result(self): ...
    @classmethod
    def wait_any(cls, rpcs): ...
    @classmethod
    def wait_all(cls, rpcs) -> None: ...

def GetDefaultAPIProxy(): ...

apiproxy: Any