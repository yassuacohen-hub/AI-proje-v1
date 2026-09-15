# -*- coding: utf-8 -*-
"""ORCH-11: Scheduler Service — cron-like task dispatch."""

from __future__ import annotations

import json
import time
import logging
from datetime import datetime
from pathlib import Path
from threading import Event, Thread
from typing import Any, Final

from company_master.orchestrator import task_board as tb

logger = logging.getLogger(__name__)

TASK_BOARD_PATH: Final[Path] = tb.ROOT / "data" / "orchestrator" / "task_board.json"
DEFAULT_INTERVAL: Final[int] = 60  # seconds


class Scheduler:
    """Cron-like task dispatcher.

    Polls the task board at a configured interval and dispatches
    tasks matching a filter to the appropriate agent.

    Args:
        interval: Poll interval in seconds. Default 60.
        filter_fn: Optional filter. If provided, only tasks where
            filter_fn(task) is True are dispatched.
        dispatch_fn: Called with (task_id, sahip) when a task is
            dispatched. Defaults to logging.
    """

    def __init__(
        self,
        interval: int = DEFAULT_INTERVAL,
        filter_fn: Any = None,
        dispatch_fn: Any = None,
    ):
        self.interval = interval
        self.filter_fn = filter_fn
        self.dispatch_fn = dispatch_fn or self._default_dispatch
        self._stop = Event()
        self._thread: Thread | None = None
        self.dispatch_log: list[dict[str, Any]] = []

    @staticmethod
    def _default_dispatch(task_id: str, sahip: str) -> None:
        logger.info("DISPATCH: %s -> %s", task_id, sahip)

    def _load_board(self) -> list[dict[str, Any]]:
        if not TASK_BOARD_PATH.exists():
            return []
        try:
            data = json.loads(TASK_BOARD_PATH.read_text(encoding="utf-8"))
            return [t for t in data if isinstance(t, dict) and "task_id" in t]
        except (json.JSONDecodeError, OSError):
            return []

    def _pending_tasks(self) -> list[dict[str, Any]]:
        """Return tasks that are plan or active and ready to dispatch."""
        board = self._load_board()
        pending = []
        for task in board:
            durum = task.get("durum")
            if durum in ("plan", "active"):
                if self.filter_fn is None or self.filter_fn(task):
                    pending.append(task)
        return pending

    def dispatch_once(self) -> int:
        """Dispatch all pending tasks once. Returns count dispatched."""
        count = 0
        for task in self._pending_tasks():
            task_id = task["task_id"]
            sahip = task.get("sahip", "unknown")
            self.dispatch_fn(task_id, sahip)
            self.dispatch_log.append({
                "ts": datetime.now().isoformat(timespec="seconds"),
                "task_id": task_id,
                "sahip": sahip,
            })
            count += 1
        return count

    def _run(self) -> None:
        """Main loop. Runs until stopped."""
        logger.info("Scheduler started (interval=%ss)", self.interval)
        while not self._stop.is_set():
            try:
                n = self.dispatch_once()
                if n:
                    logger.info("Dispatched %d tasks", n)
            except Exception as exc:
                logger.error("Scheduler error: %s", exc)
            self._stop.wait(self.interval)
        logger.info("Scheduler stopped")

    def start(self) -> "Scheduler":
        """Start the scheduler in a background thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("Scheduler already running")
            return self
        self._stop.clear()
        self._thread = Thread(target=self._run, daemon=True, name="scheduler")
        self._thread.start()
        return self

    def stop(self) -> None:
        """Stop the scheduler."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval + 5)
            self._thread = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()
        return False


def main() -> int:
    """CLI: run scheduler once (dispatch_pending) or as daemon."""
    import argparse
    parser = argparse.ArgumentParser(description="ORCH-11 Scheduler")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL, help="Poll interval seconds")
    parser.add_argument("--dry-run", action="store_true", help="List pending without dispatching")
    args = parser.parse_args()

    sched = Scheduler(interval=args.interval)

    if args.once or args.dry_run:
        pending = sched._pending_tasks()
        print(f"PENDING: {len(pending)}")
        for t in pending:
            print(f"  {t['task_id']} ({t.get('sahip', '?')}) — {t.get('baslik', '')[:60]}")
        if args.dry_run:
            return 0
        n = sched.dispatch_once()
        print(f"DISPATCHED: {n}")
        return 0

    with sched:
        print("Scheduler running. Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
