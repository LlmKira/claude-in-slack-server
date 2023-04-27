from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel


class Author(BaseModel):
    role: str


class Content(BaseModel):
    content_type: str
    parts: List[str]


class Message(BaseModel):
    id: str
    role: Optional[str]
    author: Optional[Author]
    content: Content


class ConversationRequest(BaseModel):
    action: str
    messages: List[Message]
    conversation_id: Optional[str]
    parent_message_id: str
    model: str


class ConversationResponse(BaseModel):
    message: Optional[Message]
    conversation_id: Optional[str]
    error: Optional[str]
