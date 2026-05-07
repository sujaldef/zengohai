"""Response models for the audio customer support API."""

from typing import Optional

from pydantic import BaseModel, Field


class TranscriptData(BaseModel):
    """Transcript details returned by the audio chat endpoint."""

    user_input: Optional[str] = None
    agent_response: Optional[str] = None


class AudioChatSuccessResponse(BaseModel):
    """Structured success response for audio chat requests."""

    success: bool = Field(default=True)
    audio_response: str
    transcript: TranscriptData
    processing_time_ms: int


class AudioChatErrorResponse(BaseModel):
    """Structured error response for audio chat requests."""

    success: bool = Field(default=False)
    error: str
    transcript: TranscriptData = Field(default_factory=TranscriptData)
    processing_time_ms: int


class EnhancedTextResponse(BaseModel):
    """Enhanced text response with timing data."""

    response_text: str
    processing_time_ms: int
