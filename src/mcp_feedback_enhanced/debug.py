#!/usr/bin/env python3
"""
統一調試日誌模組
================

提供統一的調試日誌功能，確保調試輸出不會干擾 MCP 通信。
所有調試輸出都會發送到 stderr，並且只在調試模式啟用時才輸出。

使用方法：
```python
from .debug import debug_log

debug_log("這是一條調試信息")
```

環境變數控制：
- MCP_DEBUG=true/1/yes/on: 啟用調試模式
- MCP_DEBUG=false/0/no/off: 關閉調試模式（默認）

作者: Minidoracat
"""

import os
import sys
from typing import Any
from datetime import datetime
from pathlib import Path


def debug_log(message: Any, prefix: str = "DEBUG") -> None:
    """
    輸出調試訊息到標準錯誤和日誌文件，避免污染標準輸出

    Args:
        message: 要輸出的調試信息
        prefix: 調試信息的前綴標識，默認為 "DEBUG"
    """
    # 只在啟用調試模式時才輸出，避免干擾 MCP 通信
    # TEMPORARILY FORCE DEBUG MODE FOR TROUBLESHOOTING
    debug_mode = True  # Force debug mode
    # debug_mode = os.getenv("MCP_DEBUG", "").lower() in ("true", "1", "yes", "on")
    if not debug_mode:
        return

    try:
        # 確保消息是字符串類型
        if not isinstance(message, str):
            message = str(message)

        # 創建帶時間戳的日誌消息
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] [{prefix}] {message}"

        # 安全地輸出到 stderr，處理編碼問題
        try:
            print(log_message, file=sys.stderr, flush=True)
        except UnicodeEncodeError:
            # 如果遇到編碼問題，使用 ASCII 安全模式
            safe_message = message.encode("ascii", errors="replace").decode("ascii")
            safe_log_message = f"[{timestamp}] [{prefix}] {safe_message}"
            print(safe_log_message, file=sys.stderr, flush=True)

        # 同時寫入日誌文件
        _write_to_log_file(log_message)

    except Exception:
        # 最後的備用方案：靜默失敗，不影響主程序
        pass


def _write_to_log_file(message: str) -> None:
    """
    將日誌消息寫入文件

    Args:
        message: 要寫入的日誌消息
    """
    try:
        # 創建日誌目錄
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # 創建日誌文件名（按日期）
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"mcp_debug_{today}.log"

        # 寫入日誌文件
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")
            f.flush()

    except Exception:
        # 如果文件寫入失敗，靜默忽略
        pass


def i18n_debug_log(message: Any) -> None:
    """國際化模組專用的調試日誌"""
    debug_log(message, "I18N")


def server_debug_log(message: Any) -> None:
    """伺服器模組專用的調試日誌"""
    debug_log(message, "SERVER")


def web_debug_log(message: Any) -> None:
    """Web UI 模組專用的調試日誌"""
    debug_log(message, "WEB")


def is_debug_enabled() -> bool:
    """檢查是否啟用了調試模式"""
    return os.getenv("MCP_DEBUG", "").lower() in ("true", "1", "yes", "on")


def set_debug_mode(enabled: bool) -> None:
    """設置調試模式（用於測試）"""
    os.environ["MCP_DEBUG"] = "true" if enabled else "false"
