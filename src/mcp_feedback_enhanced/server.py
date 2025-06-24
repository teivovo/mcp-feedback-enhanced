#!/usr/bin/env python3
"""
MCP Feedback Enhanced 伺服器主要模組

此模組提供 MCP (Model Context Protocol) 的增強回饋收集功能，
支援智能環境檢測，自動使用 Web UI 介面。

主要功能：
- MCP 工具實現
- 介面選擇（Web UI）
- 環境檢測 (SSH Remote, WSL, Local)
- 國際化支援
- 圖片處理與上傳
- 命令執行與結果展示
- 專案目錄管理

主要 MCP 工具：
- interactive_feedback: 收集用戶互動回饋
- get_system_info: 獲取系統環境資訊

作者: Fábio Ferreira (原作者)
增強: Minidoracat (Web UI, 圖片支援, 環境檢測)
重構: 模塊化設計
"""

import asyncio
import base64
import io
import json
import os
import sys
import time
from typing import Annotated, Any

from fastmcp import FastMCP
from fastmcp.utilities.types import Image as MCPImage
from mcp.types import TextContent
from pydantic import Field

# 導入統一的調試功能
from .debug import server_debug_log as debug_log

# 導入多語系支援
# 導入錯誤處理框架
from .utils.error_handler import ErrorHandler, ErrorType

# 導入資源管理器
from .utils.resource_manager import create_temp_file

# 導入 MCP 日誌中間件
from .utils.logging_middleware import (
    get_middleware,
    log_tool_start,
    log_tool_end,
    log_tool_error,
    log_session_start,
    log_session_end,
    log_mcp_tool
)

# 導入 MCP-Telegram 橋接器
from .utils.mcp_telegram_bridge import (
    get_bridge,
    initialize_bridge,
    create_telegram_session,
    end_telegram_session,
    get_telegram_feedback,
    clear_telegram_feedback
)

# 導入配置管理器
from .utils.config_manager import (
    initialize_config_manager,
    get_config_manager,
    is_telegram_enabled,
    get_telegram_config
)


# ===== 編碼初始化 =====
def init_encoding():
    """初始化編碼設置，確保正確處理中文字符"""
    try:
        # Windows 特殊處理
        if sys.platform == "win32":
            import msvcrt

            # 設置為二進制模式
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

            # 重新包裝為 UTF-8 文本流，並禁用緩衝
            # 修復 union-attr 錯誤 - 安全獲取 buffer 或 detach
            stdin_buffer = getattr(sys.stdin, "buffer", None)
            if stdin_buffer is None and hasattr(sys.stdin, "detach"):
                stdin_buffer = sys.stdin.detach()

            stdout_buffer = getattr(sys.stdout, "buffer", None)
            if stdout_buffer is None and hasattr(sys.stdout, "detach"):
                stdout_buffer = sys.stdout.detach()

            sys.stdin = io.TextIOWrapper(
                stdin_buffer, encoding="utf-8", errors="replace", newline=None
            )
            sys.stdout = io.TextIOWrapper(
                stdout_buffer,
                encoding="utf-8",
                errors="replace",
                newline="",
                write_through=True,  # 關鍵：禁用寫入緩衝
            )
        else:
            # 非 Windows 系統的標準設置
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stdin, "reconfigure"):
                sys.stdin.reconfigure(encoding="utf-8", errors="replace")

        # 設置 stderr 編碼（用於調試訊息）
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")

        return True
    except Exception:
        # 如果編碼設置失敗，嘗試基本設置
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stdin, "reconfigure"):
                sys.stdin.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except:
            pass
        return False


# 初始化編碼（在導入時就執行）
_encoding_initialized = init_encoding()

# ===== 常數定義 =====
SERVER_NAME = "互動式回饋收集 MCP"
SSH_ENV_VARS = ["SSH_CONNECTION", "SSH_CLIENT", "SSH_TTY"]
REMOTE_ENV_VARS = ["REMOTE_CONTAINERS", "CODESPACES"]


# 初始化 MCP 服務器
from . import __version__


# 確保 log_level 設定為正確的大寫格式
fastmcp_settings = {}

# 檢查環境變數並設定正確的 log_level
env_log_level = os.getenv("FASTMCP_LOG_LEVEL", "").upper()
if env_log_level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
    fastmcp_settings["log_level"] = env_log_level
else:
    # 預設使用 INFO 等級
    fastmcp_settings["log_level"] = "INFO"

mcp: Any = FastMCP(SERVER_NAME)


# ===== 工具函數 =====
def is_wsl_environment() -> bool:
    """
    檢測是否在 WSL (Windows Subsystem for Linux) 環境中運行

    Returns:
        bool: True 表示 WSL 環境，False 表示其他環境
    """
    try:
        # 檢查 /proc/version 文件是否包含 WSL 標識
        if os.path.exists("/proc/version"):
            with open("/proc/version") as f:
                version_info = f.read().lower()
                if "microsoft" in version_info or "wsl" in version_info:
                    debug_log("偵測到 WSL 環境（通過 /proc/version）")
                    return True

        # 檢查 WSL 相關環境變數
        wsl_env_vars = ["WSL_DISTRO_NAME", "WSL_INTEROP", "WSLENV"]
        for env_var in wsl_env_vars:
            if os.getenv(env_var):
                debug_log(f"偵測到 WSL 環境變數: {env_var}")
                return True

        # 檢查是否存在 WSL 特有的路徑
        wsl_paths = ["/mnt/c", "/mnt/d", "/proc/sys/fs/binfmt_misc/WSLInterop"]
        for path in wsl_paths:
            if os.path.exists(path):
                debug_log(f"偵測到 WSL 特有路徑: {path}")
                return True

    except Exception as e:
        debug_log(f"WSL 檢測過程中發生錯誤: {e}")

    return False


def is_remote_environment() -> bool:
    """
    檢測是否在遠端環境中運行

    Returns:
        bool: True 表示遠端環境，False 表示本地環境
    """
    # WSL 不應被視為遠端環境，因為它可以訪問 Windows 瀏覽器
    if is_wsl_environment():
        debug_log("WSL 環境不被視為遠端環境")
        return False

    # 檢查 SSH 連線指標
    for env_var in SSH_ENV_VARS:
        if os.getenv(env_var):
            debug_log(f"偵測到 SSH 環境變數: {env_var}")
            return True

    # 檢查遠端開發環境
    for env_var in REMOTE_ENV_VARS:
        if os.getenv(env_var):
            debug_log(f"偵測到遠端開發環境: {env_var}")
            return True

    # 檢查 Docker 容器
    if os.path.exists("/.dockerenv"):
        debug_log("偵測到 Docker 容器環境")
        return True

    # Windows 遠端桌面檢查
    if sys.platform == "win32":
        session_name = os.getenv("SESSIONNAME", "")
        if session_name and "RDP" in session_name:
            debug_log(f"偵測到 Windows 遠端桌面: {session_name}")
            return True

    # Linux 無顯示環境檢查（但排除 WSL）
    if (
        sys.platform.startswith("linux")
        and not os.getenv("DISPLAY")
        and not is_wsl_environment()
    ):
        debug_log("偵測到 Linux 無顯示環境")
        return True

    return False


def save_feedback_to_file(feedback_data: dict, file_path: str | None = None) -> str:
    """
    將回饋資料儲存到 JSON 文件

    Args:
        feedback_data: 回饋資料字典
        file_path: 儲存路徑，若為 None 則自動產生臨時文件

    Returns:
        str: 儲存的文件路徑
    """
    if file_path is None:
        # 使用資源管理器創建臨時文件
        file_path = create_temp_file(suffix=".json", prefix="feedback_")

    # 確保目錄存在
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    # 複製數據以避免修改原始數據
    json_data = feedback_data.copy()

    # 處理圖片數據：將 bytes 轉換為 base64 字符串以便 JSON 序列化
    if "images" in json_data and isinstance(json_data["images"], list):
        processed_images = []
        for img in json_data["images"]:
            if isinstance(img, dict) and "data" in img:
                processed_img = img.copy()
                # 如果 data 是 bytes，轉換為 base64 字符串
                if isinstance(img["data"], bytes):
                    processed_img["data"] = base64.b64encode(img["data"]).decode(
                        "utf-8"
                    )
                    processed_img["data_type"] = "base64"
                processed_images.append(processed_img)
            else:
                processed_images.append(img)
        json_data["images"] = processed_images

    # 儲存資料
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    debug_log(f"回饋資料已儲存至: {file_path}")
    return file_path


def create_feedback_text(feedback_data: dict) -> str:
    """
    建立格式化的回饋文字

    Args:
        feedback_data: 回饋資料字典

    Returns:
        str: 格式化後的回饋文字
    """
    text_parts = []

    # 基本回饋內容
    if feedback_data.get("interactive_feedback"):
        text_parts.append(f"=== 用戶回饋 ===\n{feedback_data['interactive_feedback']}")

    # 命令執行日誌
    if feedback_data.get("command_logs"):
        text_parts.append(f"=== 命令執行日誌 ===\n{feedback_data['command_logs']}")

    # 圖片附件概要
    if feedback_data.get("images"):
        images = feedback_data["images"]
        text_parts.append(f"=== 圖片附件概要 ===\n用戶提供了 {len(images)} 張圖片：")

        for i, img in enumerate(images, 1):
            size = img.get("size", 0)
            name = img.get("name", "unknown")

            # 智能單位顯示
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_kb = size / 1024
                size_str = f"{size_kb:.1f} KB"
            else:
                size_mb = size / (1024 * 1024)
                size_str = f"{size_mb:.1f} MB"

            img_info = f"  {i}. {name} ({size_str})"

            # 為提高兼容性，添加 base64 預覽信息
            if img.get("data"):
                try:
                    if isinstance(img["data"], bytes):
                        img_base64 = base64.b64encode(img["data"]).decode("utf-8")
                    elif isinstance(img["data"], str):
                        img_base64 = img["data"]
                    else:
                        img_base64 = None

                    if img_base64:
                        # 只顯示前50個字符的預覽
                        preview = (
                            img_base64[:50] + "..."
                            if len(img_base64) > 50
                            else img_base64
                        )
                        img_info += f"\n     Base64 預覽: {preview}"
                        img_info += f"\n     完整 Base64 長度: {len(img_base64)} 字符"

                        # 如果 AI 助手不支援 MCP 圖片，可以提供完整 base64
                        debug_log(f"圖片 {i} Base64 已準備，長度: {len(img_base64)}")

                        # 檢查是否啟用 Base64 詳細模式（從 UI 設定中獲取）
                        include_full_base64 = feedback_data.get("settings", {}).get(
                            "enable_base64_detail", False
                        )

                        if include_full_base64:
                            # 根據檔案名推斷 MIME 類型
                            file_name = img.get("name", "image.png")
                            if file_name.lower().endswith((".jpg", ".jpeg")):
                                mime_type = "image/jpeg"
                            elif file_name.lower().endswith(".gif"):
                                mime_type = "image/gif"
                            elif file_name.lower().endswith(".webp"):
                                mime_type = "image/webp"
                            else:
                                mime_type = "image/png"

                            img_info += f"\n     完整 Base64: data:{mime_type};base64,{img_base64}"

                except Exception as e:
                    debug_log(f"圖片 {i} Base64 處理失敗: {e}")

            text_parts.append(img_info)

        # 添加兼容性說明
        text_parts.append(
            "\n💡 注意：如果 AI 助手無法顯示圖片，圖片數據已包含在上述 Base64 信息中。"
        )

    return "\n\n".join(text_parts) if text_parts else "用戶未提供任何回饋內容。"


def process_images(images_data: list[dict]) -> list[MCPImage]:
    """
    處理圖片資料，轉換為 MCP 圖片對象

    Args:
        images_data: 圖片資料列表

    Returns:
        List[MCPImage]: MCP 圖片對象列表
    """
    mcp_images = []

    for i, img in enumerate(images_data, 1):
        try:
            if not img.get("data"):
                debug_log(f"圖片 {i} 沒有資料，跳過")
                continue

            # 檢查數據類型並相應處理
            if isinstance(img["data"], bytes):
                # 如果是原始 bytes 數據，直接使用
                image_bytes = img["data"]
                debug_log(
                    f"圖片 {i} 使用原始 bytes 數據，大小: {len(image_bytes)} bytes"
                )
            elif isinstance(img["data"], str):
                # 如果是 base64 字符串，進行解碼
                image_bytes = base64.b64decode(img["data"])
                debug_log(f"圖片 {i} 從 base64 解碼，大小: {len(image_bytes)} bytes")
            else:
                debug_log(f"圖片 {i} 數據類型不支援: {type(img['data'])}")
                continue

            if len(image_bytes) == 0:
                debug_log(f"圖片 {i} 數據為空，跳過")
                continue

            # 根據文件名推斷格式
            file_name = img.get("name", "image.png")
            if file_name.lower().endswith((".jpg", ".jpeg")):
                image_format = "jpeg"
            elif file_name.lower().endswith(".gif"):
                image_format = "gif"
            else:
                image_format = "png"  # 默認使用 PNG

            # 創建 MCPImage 對象
            mcp_image = MCPImage(data=image_bytes, format=image_format)
            mcp_images.append(mcp_image)

            debug_log(f"圖片 {i} ({file_name}) 處理成功，格式: {image_format}")

        except Exception as e:
            # 使用統一錯誤處理（不影響 JSON RPC）
            error_id = ErrorHandler.log_error_with_context(
                e,
                context={"operation": "圖片處理", "image_index": i},
                error_type=ErrorType.FILE_IO,
            )
            debug_log(f"圖片 {i} 處理失敗 [錯誤ID: {error_id}]: {e}")

    debug_log(f"共處理 {len(mcp_images)} 張圖片")
    return mcp_images


# ===== MCP 工具定義 =====
@mcp.tool()
async def interactive_feedback(
    project_directory: Annotated[str, Field(description="專案目錄路徑")] = ".",
    summary: Annotated[
        str, Field(description="AI 工作完成的摘要說明")
    ] = "我已完成了您請求的任務。",
    timeout: Annotated[int, Field(description="等待用戶回饋的超時時間（秒）")] = 600,
) -> list:
    """
    收集用戶的互動回饋，支援文字和圖片

    此工具使用 Web UI 介面收集用戶回饋，支援智能環境檢測。

    用戶可以：
    1. 執行命令來驗證結果
    2. 提供文字回饋
    3. 上傳圖片作為回饋
    4. 查看 AI 的工作摘要

    調試模式：
    - 設置環境變數 MCP_DEBUG=true 可啟用詳細調試輸出
    - 生產環境建議關閉調試模式以避免輸出干擾

    Args:
        project_directory: 專案目錄路徑
        summary: AI 工作完成的摘要說明
        timeout: 等待用戶回饋的超時時間（秒），預設為 600 秒（10 分鐘）

    Returns:
        List: 包含 TextContent 和 MCPImage 對象的列表
    """
    # 生成會話 ID
    session_id = f"mcp_session_{int(time.time())}_{id(project_directory)}"

    # MCP 日誌記錄 - 工具調用開始
    call_id = log_tool_start(
        "interactive_feedback",
        request_data={
            "project_directory": project_directory,
            "summary": summary,
            "timeout": timeout
        },
        session_id=session_id,
        project_directory=project_directory
    )

    # 記錄會話開始
    log_session_start(session_id, project_directory=project_directory)

    # 環境偵測
    is_remote = is_remote_environment()
    is_wsl = is_wsl_environment()

    debug_log(f"環境偵測結果 - 遠端: {is_remote}, WSL: {is_wsl}")
    debug_log("使用介面: Web UI")

    try:
        # 確保專案目錄存在
        if not os.path.exists(project_directory):
            project_directory = os.getcwd()
        project_directory = os.path.abspath(project_directory)

        # 檢查 Telegram 橋接器是否可用
        bridge = get_bridge()
        telegram_session_created = False

        if bridge and bridge.status.value == "connected":
            # 創建 Telegram 會話
            # 注意：這裡使用第一個活躍會話的 chat_id，實際應用中需要更好的會話管理
            if bridge.active_sessions:
                first_session = list(bridge.active_sessions.values())[0]
                chat_id = first_session.chat_id
                telegram_session_created = await create_telegram_session(
                    session_id, chat_id, project_directory,
                    user_context={"tool": "interactive_feedback", "summary": summary}
                )
                debug_log(f"Telegram 會話創建: {'成功' if telegram_session_created else '失敗'}")

        # 使用 Web 模式
        debug_log("回饋模式: web")

        result = await launch_web_feedback_ui(project_directory, summary, timeout)

        # 處理取消情況
        if not result:
            return [TextContent(type="text", text="用戶取消了回饋。")]

        # 儲存詳細結果
        save_feedback_to_file(result)

        # 建立回饋項目列表
        feedback_items = []

        # 添加文字回饋
        if (
            result.get("interactive_feedback")
            or result.get("command_logs")
            or result.get("images")
        ):
            feedback_text = create_feedback_text(result)
            feedback_items.append(TextContent(type="text", text=feedback_text))
            debug_log("文字回饋已添加")

        # 添加圖片回饋
        if result.get("images"):
            mcp_images = process_images(result["images"])
            # 修復 arg-type 錯誤 - 直接擴展列表
            feedback_items.extend(mcp_images)
            debug_log(f"已添加 {len(mcp_images)} 張圖片")

        # 確保至少有一個回饋項目
        if not feedback_items:
            feedback_items.append(
                TextContent(type="text", text="用戶未提供任何回饋內容。")
            )

        debug_log(f"回饋收集完成，共 {len(feedback_items)} 個項目")

        # 結束 Telegram 會話
        if telegram_session_created:
            await end_telegram_session(session_id)
            debug_log("Telegram 會話已結束")

        # 記錄會話結束
        log_session_end(session_id)

        # MCP 日誌記錄 - 工具調用成功完成
        log_tool_end(call_id, response_data={
            "feedback_items_count": len(feedback_items),
            "has_text": any(item.type == "text" for item in feedback_items),
            "has_images": any(hasattr(item, 'data') for item in feedback_items),
            "result_summary": "回饋收集成功",
            "telegram_session": telegram_session_created
        })

        return feedback_items

    except Exception as e:
        # 使用統一錯誤處理，但不影響 JSON RPC 響應
        error_id = ErrorHandler.log_error_with_context(
            e,
            context={"operation": "回饋收集", "project_dir": project_directory},
            error_type=ErrorType.SYSTEM,
        )

        # 生成用戶友好的錯誤信息
        user_error_msg = ErrorHandler.format_user_error(e, include_technical=False)
        debug_log(f"回饋收集錯誤 [錯誤ID: {error_id}]: {e!s}")

        # 結束 Telegram 會話（如果已創建）
        if 'telegram_session_created' in locals() and telegram_session_created:
            try:
                await end_telegram_session(session_id)
                debug_log("Telegram 會話已結束（錯誤情況）")
            except Exception as cleanup_error:
                debug_log(f"Telegram 會話清理失敗: {cleanup_error}")

        # 記錄會話結束
        log_session_end(session_id)

        # MCP 日誌記錄 - 工具調用錯誤
        log_tool_error(call_id, str(e), error_details={
            "error_id": error_id,
            "error_type": type(e).__name__,
            "operation": "回饋收集"
        })

        return [TextContent(type="text", text=user_error_msg)]


async def launch_web_feedback_ui(project_dir: str, summary: str, timeout: int) -> dict:
    """
    啟動 Web UI 收集回饋，支援自訂超時時間

    Args:
        project_dir: 專案目錄路徑
        summary: AI 工作摘要
        timeout: 超時時間（秒）

    Returns:
        dict: 收集到的回饋資料
    """
    debug_log(f"啟動 Web UI 介面，超時時間: {timeout} 秒")

    try:
        # 使用新的 web 模組
        from .web import launch_web_feedback_ui as web_launch

        # 傳遞 timeout 參數給 Web UI
        return await web_launch(project_dir, summary, timeout)
    except ImportError as e:
        # 使用統一錯誤處理
        error_id = ErrorHandler.log_error_with_context(
            e,
            context={"operation": "Web UI 模組導入", "module": "web"},
            error_type=ErrorType.DEPENDENCY,
        )
        user_error_msg = ErrorHandler.format_user_error(
            e, ErrorType.DEPENDENCY, include_technical=False
        )
        debug_log(f"Web UI 模組導入失敗 [錯誤ID: {error_id}]: {e}")

        return {
            "command_logs": "",
            "interactive_feedback": user_error_msg,
            "images": [],
        }


@mcp.tool()
def get_system_info() -> str:
    """
    獲取系統環境資訊

    Returns:
        str: JSON 格式的系統資訊
    """
    # MCP 日誌記錄 - 工具調用開始
    call_id = log_tool_start("get_system_info")

    try:
        is_remote = is_remote_environment()
        is_wsl = is_wsl_environment()

        system_info = {
        "平台": sys.platform,
        "Python 版本": sys.version.split()[0],
        "WSL 環境": is_wsl,
        "遠端環境": is_remote,
        "介面類型": "Web UI",
        "環境變數": {
            "SSH_CONNECTION": os.getenv("SSH_CONNECTION"),
            "SSH_CLIENT": os.getenv("SSH_CLIENT"),
            "DISPLAY": os.getenv("DISPLAY"),
            "VSCODE_INJECTION": os.getenv("VSCODE_INJECTION"),
            "SESSIONNAME": os.getenv("SESSIONNAME"),
            "WSL_DISTRO_NAME": os.getenv("WSL_DISTRO_NAME"),
            "WSL_INTEROP": os.getenv("WSL_INTEROP"),
            "WSLENV": os.getenv("WSLENV"),
        },
    }

        result = json.dumps(system_info, ensure_ascii=False, indent=2)

        # MCP 日誌記錄 - 工具調用成功完成
        log_tool_end(call_id, response_data={
            "system_info_keys": list(system_info.keys()),
            "platform": system_info["平台"],
            "is_remote": system_info["遠端環境"],
            "is_wsl": system_info["WSL 環境"]
        })

        return result

    except Exception as e:
        # MCP 日誌記錄 - 工具調用錯誤
        log_tool_error(call_id, str(e), error_details={
            "error_type": type(e).__name__,
            "operation": "系統資訊獲取"
        })
        raise


# ===== 主程式入口 =====
def main():
    """主要入口點，用於套件執行"""
    # 檢查是否啟用調試模式
    debug_enabled = os.getenv("MCP_DEBUG", "").lower() in ("true", "1", "yes", "on")

    # 檢查是否啟用桌面模式
    desktop_mode = os.getenv("MCP_DESKTOP_MODE", "").lower() in (
        "true",
        "1",
        "yes",
        "on",
    )

    if debug_enabled:
        debug_log("🚀 啟動互動式回饋收集 MCP 服務器")
        debug_log(f"   服務器名稱: {SERVER_NAME}")
        debug_log(f"   版本: {__version__}")
        debug_log(f"   平台: {sys.platform}")
        debug_log(f"   編碼初始化: {'成功' if _encoding_initialized else '失敗'}")
        debug_log(f"   遠端環境: {is_remote_environment()}")
        debug_log(f"   WSL 環境: {is_wsl_environment()}")
        debug_log(f"   桌面模式: {'啟用' if desktop_mode else '禁用'}")
        debug_log("   介面類型: Web UI")
        debug_log("   等待來自 AI 助手的調用...")

        # 初始化配置管理器
        config_manager = initialize_config_manager(
            config_file="mcp_config.json",
            enable_encryption=True,
            auto_save=True
        )
        debug_log("   配置管理器: 已初始化")

        # 初始化 MCP 日誌中間件
        from .utils.logging_middleware import initialize_middleware
        logging_config = config_manager.get_logging_config()
        middleware_config = {
            'log_level': 'debug' if debug_enabled else logging_config.level,
            'enable_telegram_forwarding': logging_config.enable_telegram_forwarding,
            'max_log_entries': logging_config.max_log_entries,
            'include_request_data': logging_config.include_request_data,
            'include_response_data': logging_config.include_response_data
        }
        middleware = initialize_middleware(middleware_config)
        debug_log("   MCP 日誌中間件: 已初始化")

        # 初始化 Telegram 橋接器（如果配置可用）
        try:
            if is_telegram_enabled():
                telegram_config = get_telegram_config()

                from .utils.telegram_manager import TelegramBotManager

                telegram_manager = TelegramBotManager(
                    telegram_config.bot_token,
                    telegram_config.chat_id
                )

                bridge_config = {
                    'session_timeout_minutes': telegram_config.session_timeout_minutes,
                    'max_concurrent_sessions': telegram_config.max_concurrent_sessions,
                    'enable_auto_forwarding': telegram_config.enable_auto_forwarding,
                    'message_format': {
                        'include_session_id': telegram_config.include_session_id,
                        'include_timestamp': telegram_config.include_timestamp,
                        'include_project_path': telegram_config.include_project_path,
                        'include_details': telegram_config.include_details
                    },
                    'chunker': {
                        'max_chunk_size': telegram_config.max_chunk_size,
                        'preserve_code_blocks': telegram_config.preserve_code_blocks,
                        'preserve_markdown': telegram_config.preserve_markdown,
                        'add_navigation': telegram_config.add_navigation,
                        'add_previews': telegram_config.add_previews
                    }
                }

                bridge = initialize_bridge(telegram_manager, middleware, bridge_config)
                debug_log("   Telegram 橋接器: 已初始化")

                # 啟動橋接器（在背景執行）
                asyncio.create_task(bridge.start())
                debug_log("   Telegram 橋接器: 已啟動")
            else:
                debug_log("   Telegram 橋接器: 未配置或已停用")

        except Exception as e:
            debug_log(f"   Telegram 橋接器初始化失敗: {e}")

        debug_log("準備啟動 MCP 伺服器...")
        debug_log("調用 mcp.run()...")

    try:
        # 使用正確的 FastMCP API
        mcp.run()
    except KeyboardInterrupt:
        if debug_enabled:
            debug_log("收到中斷信號，正常退出")
        sys.exit(0)
    except Exception as e:
        if debug_enabled:
            debug_log(f"MCP 服務器啟動失敗: {e}")
            import traceback

            debug_log(f"詳細錯誤: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
