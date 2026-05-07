"""
Base Speech-to-Text (STT) Interface

This module defines the abstract base class for Speech-to-Text implementations.
Students should implement the concrete STT class by inheriting from this base class.

Recommended implementation: Deepgram API (free tier available)
Alternative options: OpenAI Whisper, AssemblyAI, or any other STT service
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import asyncio
import io
import logging
import os
import tempfile

import librosa
import soundfile as sf
from openai import AsyncOpenAI

try:
    import whisper
except ImportError:  # pragma: no cover - optional dependency
    whisper = None


class BaseSTT(ABC):
    """
    Abstract base class for Speech-to-Text implementations.
    
    This class defines the interface that all STT implementations must follow.
    Students should inherit from this class and implement the abstract methods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the STT service.
        
        Args:
            config: Configuration dictionary containing API keys, model settings, etc.
                   Example: {"api_key": "your_api_key", "model": "nova-2"}
        """
        self.config = config or {}
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the STT service (setup API clients, load models, etc.).
        This method should be called before using the STT service.
        
        Raises:
            Exception: If initialization fails
        """
        pass
    
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, **kwargs) -> str:
        """
        Transcribe audio bytes to text.
        
        Args:
            audio_bytes: Raw audio data as bytes
            **kwargs: Additional parameters specific to the STT implementation
                     (e.g., language, model, formatting options)
        
        Returns:
            str: The transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """
        Cleanup resources (close connections, free memory, etc.).
        This method should be called when the STT service is no longer needed.
        """
        pass
    
    def is_ready(self) -> bool:
        """
        Check if the STT service is ready to use.
        
        Returns:
            bool: True if ready, False otherwise
        """
        return self.is_initialized


class STTService(BaseSTT):
    """
    Generic STT implementation template.
    
    Students should complete this implementation using their chosen STT service or pretrained model.
    
    API-based options:
    - Deepgram API (free tier, high accuracy): pip install deepgram-sdk
    - AssemblyAI (API-based): pip install assemblyai
    - Azure Speech Services: pip install azure-cognitiveservices-speech
    - Google Cloud Speech: pip install google-cloud-speech
    
    Pretrained model options (local inference):
    - OpenAI Whisper: pip install openai-whisper (various sizes: tiny, base, small, medium, large)
    - Wav2Vec2 models: pip install transformers torch (Facebook's pretrained models)
    - SpeechRecognition + offline engines: pip install SpeechRecognition pocketsphinx
    - Vosk models: pip install vosk (lightweight, supports many languages)
    - Coqui STT: pip install coqui-stt (open-source, pretrained models available)
    
    Input: audio_bytes (bytes) - Raw audio data
    Output: transcribed_text (str) - The text transcription
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.client = None
        self.logger = logging.getLogger(__name__)
        self.model = self.config.get("model", "whisper-1")
        self.timeout = self.config.get("timeout", 60)
        self.language = self.config.get("language")
        self.prompt = self.config.get("prompt")
        self.backend = self.config.get("backend")
    
    async def initialize(self) -> None:
        """Initialize either local Whisper or the OpenAI transcription client."""
        try:
            use_openai = self.backend == "openai" or self.model == "whisper-1"

            if use_openai:
                api_key = self.config.get("api_key") or os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OpenAI API key not provided")

                base_url = self.config.get("base_url")
                self.client = AsyncOpenAI(
                    api_key=api_key,
                    base_url=base_url,
                    timeout=self.timeout,
                )
                self.backend = "openai"
            else:
                if whisper is None:
                    raise ImportError(
                        "openai-whisper is required for local STT. Install it with `pip install openai-whisper`."
                    )
                self.client = whisper.load_model(self.model)
                self.backend = "local_whisper"

            self.is_initialized = True
            self.logger.info("STT service initialized successfully")

        except Exception:
            self.logger.exception("Failed to initialize STT service")
            raise
    
    async def transcribe(self, audio_bytes: bytes, **kwargs) -> str:
        """
        TODO: Implement audio transcription.
        
        Input: audio_bytes (bytes) - Raw audio data in any supported format
        Output: str - Transcribed text
        
        Steps:
        1. Check if service is initialized
        2. Prepare audio data for your chosen service
        3. Call transcription API/model
        4. Extract and return transcribed text
        5. Handle errors appropriately
        
        Example implementations:
        
        For Deepgram:
        ```python
        response = await self.client.listen.prerecorded.v("1").transcribe_file(
            {"buffer": audio_bytes}, 
            {"model": "nova-2", "smart_format": True}
        )
        return response["results"]["channels"][0]["alternatives"][0]["transcript"]
        ```
        
        For Whisper (pretrained model):
        ```python
        import io
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            result = self.client.transcribe(temp_file.name)
            return result["text"]
        ```
        
        For Wav2Vec2 (Transformers):
        ```python
        import torch
        import torchaudio
        # Convert bytes to tensor, resample if needed
        waveform, sample_rate = torchaudio.load(io.BytesIO(audio_bytes))
        inputs = self.processor(waveform.squeeze(), sampling_rate=16000, return_tensors="pt")
        with torch.no_grad():
            logits = self.client(**inputs).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        return self.processor.decode(predicted_ids[0])
        ```
        
        For AssemblyAI (API):
        ```python
        transcriber = assemblyai.Transcriber()
        transcript = transcriber.transcribe(audio_bytes)
        return transcript.text
        ```
        """
        if not self.is_ready():
            raise RuntimeError("STT service not initialized")
        
        if not audio_bytes:
            raise ValueError("Audio data cannot be empty")

        try:
            if self.backend == "openai":
                audio_file = io.BytesIO(audio_bytes)
                audio_file.name = kwargs.get("filename", "audio.wav")

                transcription_kwargs = {
                    "model": kwargs.get("model", self.model),
                    "file": audio_file,
                }

                if self.language or kwargs.get("language"):
                    transcription_kwargs["language"] = kwargs.get("language", self.language)
                if self.prompt or kwargs.get("prompt"):
                    transcription_kwargs["prompt"] = kwargs.get("prompt", self.prompt)

                result = await self.client.audio.transcriptions.create(**transcription_kwargs)
                text = getattr(result, "text", "")
                return text.strip()

            transcription_options = {
                "language": kwargs.get("language", self.language),
                "fp16": kwargs.get("fp16", False),
            }
            if self.prompt or kwargs.get("prompt"):
                transcription_options["initial_prompt"] = kwargs.get("prompt", self.prompt)

            try:
                audio_array, sample_rate = sf.read(io.BytesIO(audio_bytes), dtype="float32", always_2d=False)

                # Convert multi-channel audio to mono.
                if getattr(audio_array, "ndim", 1) > 1:
                    audio_array = audio_array.mean(axis=1)

                if sample_rate != 16000:
                    audio_array = librosa.resample(audio_array, orig_sr=sample_rate, target_sr=16000)

                result = await asyncio.to_thread(
                    self.client.transcribe,
                    audio_array,
                    **{key: value for key, value in transcription_options.items() if value is not None},
                )
                return result.get("text", "").strip()

            except Exception:
                # Fallback for formats not decoded by soundfile (may require ffmpeg).
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_file.write(audio_bytes)
                    temp_path = temp_file.name

                try:
                    result = await asyncio.to_thread(
                        self.client.transcribe,
                        temp_path,
                        **{key: value for key, value in transcription_options.items() if value is not None},
                    )
                    return result.get("text", "").strip()
                except FileNotFoundError as file_error:
                    raise RuntimeError(
                        "FFmpeg is missing on Windows for this audio format. "
                        "Install ffmpeg or upload WAV audio."
                    ) from file_error
                finally:
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass

        except Exception:
            self.logger.exception("STT transcription failed")
            raise
    
    async def cleanup(self) -> None:
        """Close the async client and reset the service state."""
        try:
            if self.client is not None and hasattr(self.client, "close"):
                await self.client.close()
        finally:
            self.client = None
            self.is_initialized = False