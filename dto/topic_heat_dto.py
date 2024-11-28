from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TopicNotifyResult:
    id: int
    television: str
    category: str
    keyword: str
    heat: int
    created_at: datetime


@dataclass
class HeatData:
    current_heat: int
    previous_heat: int
    diff: int
    current_time: datetime
    previous_time: Optional[datetime]
    id: int
    television: str
    category: str