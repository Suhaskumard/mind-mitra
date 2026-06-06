from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class JournalEntryBase(BaseModel):
    mood: int = Field(..., ge=1, le=10)
    text: str = Field(..., min_length=1)
    date: Optional[datetime] = None


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryUpdate(BaseModel):
    mood: Optional[int] = Field(None, ge=1, le=10)
    text: Optional[str] = Field(None, min_length=1)
    date: Optional[datetime] = None


class JournalEntry(JournalEntryBase):
    id: str
    user_id: str
    date: datetime


class MoodHistoryPoint(BaseModel):
    date: datetime
    mood: float


class MoodHistoryResponse(BaseModel):
    user_id: str
    period_days: int
    average_mood: Optional[float] = None
    entries: List[MoodHistoryPoint]
