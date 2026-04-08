import sys
from loguru import logger
from .context import get_trace_id
from daos import LogDAO 

def database_sink(message):
    record = message.record
    trace_id = record["extra"].get("trace_id", get_trace_id())
    route = record["extra"].get("route")
    method = record["extra"].get("method")
    
    LogDAO().create(
        trace_id=trace_id,
        level=record["level"].name,
        message=record["message"],
        route=route,
        method=method
    )

def custom_format(record):
    trace_id = record["extra"].get("trace_id") or get_trace_id() or "N/A"
    record["extra"]["trace_id"] = trace_id
    
    return "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | Trace: <cyan>{extra[trace_id]}</cyan> | <level>{message}</level>\n"

logger.remove()

logger.add(sys.stdout, format=custom_format, level="INFO")

logger.add(database_sink, level="INFO")

custom_log = logger