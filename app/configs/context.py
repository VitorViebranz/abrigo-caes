from contextvars import ContextVar
from starlette.requests import Request

_request_ctx_var: ContextVar[Request | None] = ContextVar("request", default=None)
_trace_id_ctx_var: ContextVar[str | None] = ContextVar("trace_id", default=None)

def set_request(request: Request):
    _request_ctx_var.set(request)

def set_trace_id(trace_id: str):
    _trace_id_ctx_var.set(trace_id)

def get_trace_id() -> str | None:
    return _trace_id_ctx_var.get()