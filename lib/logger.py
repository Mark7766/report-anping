from __future__ import annotations

# -*- coding: utf-8 -*-
"""
report-anping — 统一日志管理（无 Flask 依赖）

日志格式: [时间] [请求ID] [模块] [级别] [消息] {上下文JSON}
"""

import json
import logging
import os
import sys
import threading
import uuid
from datetime import datetime

# 线程本地存储，用于存储请求ID
_request_context = threading.local()

# 全局日志配置标志
_logging_configured = False


def get_request_id() -> str:
    """获取当前请求ID（纯 stdlib，无 Flask 依赖）。"""
    if hasattr(_request_context, "request_id"):
        return _request_context.request_id
    return "-"


def set_request_id(request_id: str | None = None) -> str:
    """设置请求ID（用于非HTTP请求场景，如后台任务）。"""
    if request_id is None:
        request_id = str(uuid.uuid4())[:8]
    _request_context.request_id = request_id
    return request_id


class RequestIdFilter(logging.Filter):
    """日志过滤器，添加请求ID到日志记录。"""

    def filter(self, record: logging.LogRecord) -> bool:
        """Attach request_id to every log record."""
        record.request_id = get_request_id()
        return True


class JsonContextFormatter(logging.Formatter):
    """
    自定义日志格式化器。
    格式: [时间] [请求ID] [模块] [级别] [消息] {上下文JSON}
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record into a structured string."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        request_id = getattr(record, "request_id", "-")
        module = record.name
        level = record.levelname
        message = record.getMessage()

        log_line = f"[{timestamp}] [{request_id}] [{module}] [{level}] {message}"

        context = getattr(record, "context", None)
        if context:
            try:
                context_json = json.dumps(context, ensure_ascii=False, default=str)
                log_line += f" {context_json}"
            except (TypeError, ValueError):
                pass

        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)

        return log_line


class ContextLogger:
    """支持上下文的日志记录器，可附加结构化上下文数据。"""

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize with an underlying stdlib logger."""
        self._logger = logger

    def _log(
        self,
        level: int,
        message: str,
        context: dict | None = None,
        exc_info: bool = False,
    ) -> None:
        """内部日志方法。"""
        extra = {"context": context} if context else {}
        self._logger.log(level, message, extra=extra, exc_info=exc_info)

    def debug(self, message: str, context: dict | None = None) -> None:
        """调试日志。"""
        self._log(logging.DEBUG, message, context)

    def info(self, message: str, context: dict | None = None) -> None:
        """信息日志。"""
        self._log(logging.INFO, message, context)

    def warning(self, message: str, context: dict | None = None) -> None:
        """警告日志。"""
        self._log(logging.WARNING, message, context)

    def warn(self, message: str, context: dict | None = None) -> None:
        """警告日志（别名）。"""
        self.warning(message, context)

    def error(self, message: str, context: dict | None = None, exc_info: bool = False) -> None:
        """错误日志。"""
        self._log(logging.ERROR, message, context, exc_info=exc_info)

    def critical(self, message: str, context: dict | None = None, exc_info: bool = False) -> None:
        """严重错误日志。"""
        self._log(logging.CRITICAL, message, context, exc_info=exc_info)

    def exception(self, message: str, context: dict | None = None) -> None:
        """异常日志（自动附加异常信息）。"""
        self._log(logging.ERROR, message, context, exc_info=True)


def _setup_logging() -> None:
    """配置全局日志系统（幂等，只执行一次）。"""
    global _logging_configured
    if _logging_configured:
        return
    _logging_configured = True

    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if root_logger.handlers:
        root_logger.handlers.clear()

    request_id_filter = RequestIdFilter()

    log_file = os.path.join(log_dir, f"report_anping_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.addFilter(request_id_filter)
    file_handler.setFormatter(JsonContextFormatter())

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.addFilter(request_id_filter)
    console_handler.setFormatter(JsonContextFormatter())

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    root_logger.info("日志系统初始化完成")


def get_logger(name: str = "report_anping") -> ContextLogger:
    """
    获取日志实例。

    Args:
        name: 日志器名称（模块名）

    Returns:
        ContextLogger: 支持上下文的日志器

    使用示例:
        logger = get_logger('docx_builder')
        logger.info('文档创建成功', {'output': 'report.docx'})
    """
    _setup_logging()
    return ContextLogger(logging.getLogger(name))
