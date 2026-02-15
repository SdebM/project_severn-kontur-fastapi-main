"""Инициализация пакета routers.

Позволяет импортировать подмодули как `from app.routers import users, auth`.
"""

from . import users, auth

__all__ = ["users", "auth"]
