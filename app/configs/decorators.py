from functools import wraps
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

            if request:
                logger.info(
                    f"[{request.method} {request.url.path}] Requisição recebida | IP: {request.client.host}"
                )

            try:
                return await handler(*args, **kwargs)
            except HTTPException as http_exc:
                logger.warning(
                    f"[{request.url.path}] HTTPException capturada: {http_exc.detail}"
                    if request
                    else f"HTTPException capturada: {http_exc.detail}"
                )
                raise http_exc
            except ValidationError as val_err:
                logger.error(
                    f"[{request.url.path}] Erro de validação Pydantic: {val_err.errors()}"
                    if request
                    else "Erro de validação Pydantic"
                )
                raise HTTPException(
                    status_code=422, detail="Campo inválido ou não informado."
                )
            except Exception:
                logger.exception(
                    f"[{request.url.path}] Erro inesperado na rota"
                    if request
                    else "Erro inesperado na rota"
                )
                raise HTTPException(status_code=500, detail="Erro interno no servidor")

        return async_wrapper

    @wraps(handler)
    def sync_wrapper(*args, **kwargs):
        request = _extract_request(handler, args, kwargs)

        if request:
            logger.info(
                f"[{request.method} {request.url.path}] Requisição recebida | IP: {request.client.host}"
            )

        try:
            return handler(*args, **kwargs)
        except HTTPException as http_exc:
            logger.warning(
                f"[{request.url.path}] HTTPException capturada: {http_exc.detail}"
                if request
                else f"HTTPException capturada: {http_exc.detail}"
            )
            raise http_exc
        except ValidationError as val_err:
            logger.error(
                f"[{request.url.path}] Erro de validação Pydantic: {val_err.errors()}"
                if request
                else "Erro de validação Pydantic"
            )
            raise HTTPException(
                status_code=422, detail="Campo inválido ou não informado."
            )
        except Exception:
            logger.exception(
                f"[{request.url.path}] Erro inesperado na rota"
                if request
                else "Erro inesperado na rota"
            )
            raise HTTPException(status_code=500, detail="Erro interno no servidor")
        finally:
            logger.info(
                f"[{request.method} {request.url.path}] Requisição finalizada | IP: {request.client.host}"
                if request
                else "Requisição finalizada"
            )

    return sync_wrapper