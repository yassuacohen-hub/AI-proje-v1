# -*- coding: utf-8 -*-
"""Event bus for async task processing.

Kullanim:
    from src.company_master.queue.event_bus import EventBus

    bus = EventBus()
    bus.subscribe("task.created", handler_func)
    bus.emit("task.created", {"task_id": "T1"})
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

from src.company_master.queue.message_queue import RedisMessageQueue


class EventBus:
    """Event-driven async processing bus."""

    def __init__(self, queue: RedisMessageQueue = None):
        self._queue = queue or RedisMessageQueue()
        self._handlers: dict[str, list[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> bool:
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                return True
            except ValueError:
                return False
        return False

    def emit(self, event_type: str, data: dict[str, Any]) -> int:
        self._queue.publish(event_type, data)
        return len(self._handlers.get(event_type, []))

    def emit_batch(self, event_type: str, events: list[dict[str, Any]]) -> int:
        count = 0
        for event in events:
            if self.emit(event_type, event):
                count += 1
        return count

    def process(self, event_type: str) -> int:
        """Process all pending events for a type."""
        count = 0
        while self._queue.size(event_type) > 0:
            msg = self._queue.consume(event_type)
            if not msg:
                break
            data = msg.get("data", {})
            for handler in self._handlers.get(event_type, []):
                try:
                    handler(data)
                    count += 1
                except Exception:
                    pass
        return count

    def get_subscribers(self, event_type: str) -> int:
        return len(self._handlers.get(event_type, []))

    def list_topics(self) -> list[str]:
        return list(self._handlers.keys())


__all__ = ["EventBus"]
