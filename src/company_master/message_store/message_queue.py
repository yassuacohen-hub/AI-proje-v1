# -*- coding: utf-8 -*-
"""Message queue based on Redis.

Kullanim:
    from src.company_master.queue.message_queue import RedisMessageQueue

    q = RedisMessageQueue()
    q.publish("task.created", {"task_id": "T1", "type": "scan"})
    msg = q.consume("task.created")
"""
from __future__ import annotations

import json
import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))


class MessageQueue(ABC):
    """Abstract message queue."""

    @abstractmethod
    def publish(self, topic: str, message: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def consume(self, topic: str, timeout: float = 5.0) -> Optional[dict[str, Any]]:
        pass

    @abstractmethod
    def size(self, topic: str) -> int:
        pass


class RedisMessageQueue(MessageQueue):
    """Redis tabanli mesaj kuyrugu."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self._host = host
        self._port = port
        self._db = db
        self._redis = None
        self._fallback: dict[str, list[dict]] = {}

    def _connect(self):
        if self._redis is None:
            try:
                import redis
                self._redis = redis.Redis(
                    host=self._host, port=self._port, db=self._db,
                    socket_timeout=2, socket_connect_timeout=2,
                )
                self._redis.ping()
            except Exception:
                self._redis = None

    def _get_fallback(self) -> dict[str, list[dict]]:
        return self._fallback

    def publish(self, topic: str, message: dict[str, Any]) -> bool:
        payload = json.dumps({
            "topic": topic,
            "data": message,
            "timestamp": time.time(),
            "id": f"{topic}:{int(time.time() * 1000)}",
        })

        self._connect()
        if self._redis:
            try:
                self._redis.rpush(f"mq:{topic}", payload)
                return True
            except Exception:
                pass

        # Fallback
        self._fallback.setdefault(topic, []).append(json.loads(payload))
        return True

    def consume(self, topic: str, timeout: float = 5.0) -> Optional[dict[str, Any]]:
        self._connect()

        if self._redis:
            try:
                result = self._redis.lpop(f"mq:{topic}")
                if result:
                    return json.loads(result)
            except Exception:
                pass

        queue = self._fallback.get(topic, [])
        if queue:
            return queue.pop(0)

        return None

    def size(self, topic: str) -> int:
        self._connect()
        if self._redis:
            try:
                return self._redis.llen(f"mq:{topic}")
            except Exception:
                pass
        return len(self._fallback.get(topic, []))

    def publish_batch(self, topic: str, messages: list[dict[str, Any]]) -> int:
        count = 0
        for msg in messages:
            if self.publish(topic, msg):
                count += 1
        return count

    def peek(self, topic: str) -> Optional[dict[str, Any]]:
        self._connect()
        if self._redis:
            try:
                result = self._redis.lindex(f"mq:{topic}", 0)
                if result:
                    return json.loads(result)
            except Exception:
                pass
        queue = self._fallback.get(topic, [])
        if queue:
            return queue[0]
        return None


__all__ = ["MessageQueue", "RedisMessageQueue"]
