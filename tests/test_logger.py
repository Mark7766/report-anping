from __future__ import annotations

"""
Tests for lib/logger.py — pure stdlib log layer, no Flask dependency.
"""

import sys
from pathlib import Path

# Allow `from lib.xxx import` when running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.logger import (
    ContextLogger,
    get_logger,
    get_request_id,
    set_request_id,
)


class TestRequestId:
    """Tests for thread-local request ID helpers."""

    def test_default_returns_dash(self) -> None:
        """Without setting, get_request_id() returns '-'."""
        import threading

        from lib import logger as logger_mod

        result: list[str] = []

        def worker() -> None:
            # Clear any lingering state in this thread
            if hasattr(logger_mod._request_context, "request_id"):
                del logger_mod._request_context.request_id
            result.append(get_request_id())

        t = threading.Thread(target=worker)
        t.start()
        t.join()
        assert result[0] == "-"

    def test_set_and_get(self) -> None:
        """set_request_id stores and get_request_id retrieves the value."""
        rid = set_request_id("test-1234")
        assert rid == "test-1234"
        assert get_request_id() == "test-1234"

    def test_auto_generate(self) -> None:
        """set_request_id without argument generates a UUID fragment."""
        rid = set_request_id()
        assert len(rid) == 8
        assert get_request_id() == rid

    def test_thread_isolation(self) -> None:
        """Request IDs are isolated per thread."""
        import threading

        set_request_id("main-thread")
        child_result: list[str] = []

        def child() -> None:
            set_request_id("child-thread")
            child_result.append(get_request_id())

        t = threading.Thread(target=child)
        t.start()
        t.join()

        assert child_result[0] == "child-thread"
        assert get_request_id() == "main-thread"


class TestContextLogger:
    """Tests for ContextLogger wrapper."""

    def test_get_logger_returns_context_logger(self) -> None:
        """get_logger() returns a ContextLogger instance."""
        logger = get_logger("test_module")
        assert isinstance(logger, ContextLogger)

    def test_info_does_not_raise(self, capfd) -> None:
        """Calling info() doesn't raise; produces output."""
        logger = get_logger("test_info")
        logger.info("test message")

    def test_debug_with_context(self) -> None:
        """debug() accepts a context dict without error."""
        logger = get_logger("test_debug")
        logger.debug("debug msg", context={"key": "value"})

    def test_warning_alias(self) -> None:
        """warn() is an alias for warning() and does not raise."""
        logger = get_logger("test_warn")
        logger.warn("warn alias test")

    def test_error_without_exc_info(self) -> None:
        """error() without exc_info=True does not raise."""
        logger = get_logger("test_error")
        logger.error("error message", context={"code": 500})

    def test_exception_logs_traceback(self) -> None:
        """exception() logs with exc_info and doesn't raise."""
        logger = get_logger("test_exception")
        try:
            raise ValueError("test exception")
        except ValueError:
            logger.exception("caught exception")

    def test_same_name_returns_same_underlying_logger(self) -> None:
        """Two get_logger calls with same name share underlying stdlib logger."""
        a = get_logger("shared")
        b = get_logger("shared")
        assert a._logger is b._logger
