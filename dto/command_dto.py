from dataclasses import dataclass
from typing import Callable, Tuple, List, Optional


@dataclass
class CommandContext:
    """命令上下文"""
    content: str
    talker_wxid: str = ''  # 群 ID
    sender_wxid: str = ''  # 群发送人 ID
    bytes_extra: str = ''  # 扩展字段BASE64后的二进制数据


@dataclass
class Command:
    """命令配置类"""
    prefixes: Tuple[str, ...]
    handler: Callable
    require_content: bool = True
    description: str = ""
    hidden: bool = False
    is_admin: bool = False
