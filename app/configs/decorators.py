import inspect
from functools import wraps
from fastapi import Request, HTTPException
from configs.logger import custom_log
from configs.context import get_trace_id

def route_logger():
    def decorator(func):
        
        def _get_logger_and_log_start(*args, **kwargs):
            request: Request = kwargs.get("request") or next((arg for arg in args if isinstance(arg, Request)), None)
            route = request.url.path if request else func.__name__
            method = request.method if request else "N/A"
            
            t_id = get_trace_id()
            if not t_id and request and hasattr(request.state, "trace_id"):
                t_id = request.state.trace_id
                
            bound_logger = custom_log.bind(route=route, method=method, trace_id=t_id or "N/A")
            bound_logger.info(f"Iniciando requisição [{method}] {route}")
            return bound_logger

        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                bound_logger = _get_logger_and_log_start(*args, **kwargs)
                try:
                    response = await func(*args, **kwargs)
                    bound_logger.info("Requisição finalizada com sucesso.")
                    return response
                except Exception as e:
                    bound_logger.exception(f"Exceção capturada na rota: {str(e)}")
                    if isinstance(e, HTTPException):
                        raise e
                    raise HTTPException(status_code=500, detail="Erro interno no servidor.")
            return async_wrapper

        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                bound_logger = _get_logger_and_log_start(*args, **kwargs)
                try:
                    response = func(*args, **kwargs)
                    bound_logger.info("Requisição finalizada com sucesso.")
                    return response
                except Exception as e:
                    bound_logger.exception(f"Exceção capturada na rota: {str(e)}")
                    if isinstance(e, HTTPException):
                        raise e
                    raise HTTPException(status_code=500, detail="Erro interno no servidor.")
            return sync_wrapper

    return decorator