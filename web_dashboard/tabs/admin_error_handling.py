# -*- coding: utf-8 -*-
"""Admin tabs ortak logging yardımcıları.

Sessiz `except: pass` kalıplarını düzenli loglamaya çevirir.
"""
from __future__ import annotations

import logging
import traceback
from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

# Admin tabs logger
_admin_logger = logging.getLogger("admin_tabs")
if not _admin_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))
    _admin_logger.addHandler(handler)
    _admin_logger.setLevel(logging.WARNING)


def log_exception(
    logger: logging.Logger | None = None,
    message: str = "Beklenmeyen hata",
    level: int = logging.WARNING,
    reraise: bool = False,
) -> Callable[[F], F]:
    """Decorator: fonksiyon içindeki exception'ları loglar.

    Args:
        logger: Kullanılacak logger (None ise admin_tabs logger)
        message: Log mesajı öneki
        level: Log seviyesi
        reraise: True ise exception tekrar fırlatılır
    """
    log = logger or _admin_logger

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                log.log(
                    level,
                    "%s: %s — %s",
                    message,
                    exc.__class__.__name__,
                    exc,
                )
                log.debug("Stack trace:", exc_info=exc)
                if reraise:
                    raise
                return None
        return wrapper  # type: ignore
    return decorator


def silent_except_replacement(
    message: str = "İşlem başarısız",
    level: int = logging.WARNING,
    default_return: Any = None,
) -> Callable[[F], F]:
    """Sessiz `except Exception: pass` yerine geçen decorator.

    Eski kalıp:
        try:
            ...
        except Exception:
            pass

    Yeni kalıp:
        @silent_except_replacement("Veri yüklenemedi")
        def fonksiyon():
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                _admin_logger.log(
                    logging.WARNING,
                    "%s: %s — %s",
                    message,
                    exc.__class__.__name__,
                    exc,
                )
                _admin_logger.debug("Stack trace:", exc_info=exc)
                return default_return
        return wrapper  # type: ignore
    return decorator


def log_and_return_default(
    message: str,
    default: Any = None,
    level: int = logging.WARNING,
) -> Any:
    """Context manager yerine basit yardımcı: loglar ve default döner.

    Kullanım:
        try:
            return riskli_islem()
        except Exception as exc:
            return log_and_return_default("İşlem başarısız", default=[])
    """
    _admin_logger.log(
        level,
        "%s: %s — %s",
        message,
        exc.__class__.__name__ if 'exc' in locals() else "Exception",
        exc if 'exc' in locals() else "Unknown",
    )
    return default


class AdminErrorHandler:
    """Admin tabs için merkezi hata işleme sınıfı."""

    def __init__(self, module_name: str):
        self.logger = logging.getLogger(f"admin_tabs.{module_name}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            ))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.WARNING)

    def handle(self, message: str, exc: Exception, default: Any = None) -> Any:
        self.logger.warning("%s: %s — %s", message, exc.__class__.__name__, exc)
        self.logger.debug("Stack trace:", exc_info=exc)
        return None

    def warning(self, message: str, exc: Exception) -> None:
        self.logger.warning("%s: %s — %s", message, exc.__class__.__name__, exc)
        self.logger.debug("Stack trace:", exc_info=exc)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def debug(self, message: str) -> None:
        self.logger.debug(message)
