from functools import wraps
import time
from fastapi import HTTPException, Request
from inspect import signature, iscoroutinefunction
from pydantic import ValidationError
from loguru import logger


def _extract_request(handler, args, kwargs) -> Request | None:
    request = kwargs.get("request")
    if isinstance(request, Request):
        return request

    for arg in args:
        if isinstance(arg, Request):
            return arg

    sig = signature(handler)
    bound = sig.bind_partial(*args, **kwargs)
    for value in bound.arguments.values():
        if isinstance(value, Request):
            return value

    return None


def route_logger(handler):
    if iscoroutinefunction(handler):
        @wraps(handler)
        async def async_wrapper(*args, **kwargs):
            request = _extract_request(handler, args, kwargs)
            log = logger.bind(
                route=request.url.path if request else None,
                method=request.method if request else None,
            )
            start = time.perf_counter()

            try:
                response = await handler(*args, **kwargs)
                status_code = getattr(response, "status_code", 200)
                duration_ms = (time.perf_counter() - start) * 1000
                log.info(
                    f"[{request.method} {request.url.path}] {status_code} em {duration_ms:.2f}ms"
                    if request
                    else f"Request finalizada {status_code} em {duration_ms:.2f}ms"
                )
                return response
            except HTTPException as http_exc:
                duration_ms = (time.perf_counter() - start) * 1000
                log.warning(
                    f"[{request.url.path}] HTTPException capturada: {http_exc.detail}"
                    if request
                    else f"HTTPException capturada: {http_exc.detail}"
                )
                raise http_exc
            except ValidationError as val_err:
                duration_ms = (time.perf_counter() - start) * 1000
                log.error(
                    f"[{request.url.path}] Erro de validação Pydantic: {val_err.errors()}"
                    if request
                    else "Erro de validação Pydantic"
                )
                raise HTTPException(
                    status_code=422, detail="Campo inválido ou não informado."
                )
            except Exception:
                duration_ms = (time.perf_counter() - start) * 1000
                log.exception(
                    f"[{request.url.path}] Erro inesperado na rota"
                    if request
                    else "Erro inesperado na rota"
                )
                raise HTTPException(status_code=500, detail="Erro interno no servidor")

        return async_wrapper

    @wraps(handler)
    def sync_wrapper(*args, **kwargs):
        request = _extract_request(handler, args, kwargs)
        log = logger.bind(
            route=request.url.path if request else None,
            method=request.method if request else None,
        )
        start = time.perf_counter()

        try:
            response = handler(*args, **kwargs)
            status_code = getattr(response, "status_code", 200)
            duration_ms = (time.perf_counter() - start) * 1000
            log.info(
                f"[{request.method} {request.url.path}] {status_code} em {duration_ms:.2f}ms"
                if request
                else f"Request finalizada {status_code} em {duration_ms:.2f}ms"
            )
            return response
        except HTTPException as http_exc:
            duration_ms = (time.perf_counter() - start) * 1000
            log.warning(
                f"[{request.url.path}] HTTPException capturada: {http_exc.detail}"
                if request
                else f"HTTPException capturada: {http_exc.detail}"
            )
            raise http_exc
        except ValidationError as val_err:
            duration_ms = (time.perf_counter() - start) * 1000
            log.error(
                f"[{request.url.path}] Erro de validação Pydantic: {val_err.errors()}"
                if request
                else "Erro de validação Pydantic"
            )
            raise HTTPException(
                status_code=422, detail="Campo inválido ou não informado."
            )
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            log.exception(
                f"[{request.url.path}] Erro inesperado na rota"
                if request
                else "Erro inesperado na rota"
            )
            raise HTTPException(status_code=500, detail="Erro interno no servidor")

    return sync_wrapper