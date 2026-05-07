"""Audio Customer Support Agent pipeline orchestration."""

import asyncio
import time
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from src.stt.base_stt import BaseSTT, STTService
from src.llm.agent import BaseAgent, CustomerSupportAgent
from src.tts.base_tts import BaseTTS, TTSService


@dataclass
class PipelineConfig:
    """Configuration for the audio support pipeline."""
    stt_config: Dict[str, Any]
    llm_config: Dict[str, Any]
    tts_config: Dict[str, Any]
    enable_logging: bool = True


@dataclass
class AudioTranscript:
    """Transcript metadata captured from the audio pipeline."""

    user_input: Optional[str] = None
    agent_response: Optional[str] = None


@dataclass
class AudioProcessingResult:
    """Structured result returned by the audio pipeline."""

    success: bool
    audio_bytes: bytes
    transcript: AudioTranscript
    processing_time_ms: int


class AudioPipelineError(RuntimeError):
    """Raised when a pipeline stage fails after timing has started."""

    def __init__(
        self,
        message: str,
        *,
        processing_time_ms: int,
        user_input: Optional[str] = None,
        agent_response: Optional[str] = None,
    ):
        super().__init__(message)
        self.processing_time_ms = processing_time_ms
        self.user_input = user_input
        self.agent_response = agent_response


class AudioSupportPipeline:
    """
    Main pipeline class that orchestrates STT -> LLM -> TTS flow.
    
    This class manages the entire audio processing pipeline for customer support.
    Students should complete the implementation to make it fully functional.
    """
    
    def __init__(self, config: PipelineConfig):
        """
        Initialize the audio support pipeline.
        
        Args:
            config: Pipeline configuration containing settings for all components
        """
        self.config = config
        self.stt: Optional[BaseSTT] = None
        self.llm_agent: Optional[BaseAgent] = None
        self.tts: Optional[BaseTTS] = None
        self.is_initialized = False
        
        if config.enable_logging:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.CRITICAL)
    
    async def initialize(self) -> None:
        """Initialize STT, LLM, and TTS components."""
        try:
            self.logger.info("Initializing Audio Support Pipeline...")
            
            self.logger.info("Initializing STT service...")
            self.stt = STTService(self.config.stt_config)
            await self.stt.initialize()
            
            self.logger.info("Initializing LLM agent...")
            self.llm_agent = CustomerSupportAgent(self.config.llm_config)
            await self.llm_agent.initialize()
            
            self.logger.info("Initializing TTS service...")
            self.tts = TTSService(self.config.tts_config)
            await self.tts.initialize()
            
            if not all([self.stt.is_ready(), self.llm_agent.is_initialized, self.tts.is_ready()]):
                raise RuntimeError("Some pipeline components failed to initialize")
            
            self.is_initialized = True
            self.logger.info("Pipeline initialized successfully!")
            
        except Exception as e:
            self.logger.error(f"Pipeline initialization failed: {str(e)}")
            await self.cleanup()
            raise
    
    async def process_audio(self, audio_bytes: bytes, **kwargs) -> AudioProcessingResult:
        """Process audio input through the complete pipeline."""
        if not self.is_initialized:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        
        start_time = time.perf_counter()
        user_input: Optional[str] = None
        agent_response: Optional[str] = None

        try:
            self.logger.info("Converting speech to text...")
            user_input = await self.stt.transcribe(audio_bytes, **kwargs)
            self.logger.info("Transcribed text: %s", user_input)
            
            self.logger.info("Processing query with LLM agent...")
            agent_response = await self.llm_agent.process_query(user_input, **kwargs)
            self.logger.info("Agent response: %s", agent_response)
            
            self.logger.info("Converting response to speech...")
            response_audio = await self.tts.synthesize(agent_response, **kwargs)
            self.logger.info("Audio response generated successfully")
            
            processing_time_ms = int((time.perf_counter() - start_time) * 1000)
            return AudioProcessingResult(
                success=True,
                audio_bytes=response_audio,
                transcript=AudioTranscript(
                    user_input=user_input,
                    agent_response=agent_response,
                ),
                processing_time_ms=processing_time_ms,
            )
            
        except Exception as e:
            processing_time_ms = int((time.perf_counter() - start_time) * 1000)
            self.logger.error("Pipeline processing failed: %s", str(e))
            raise AudioPipelineError(
                str(e),
                processing_time_ms=processing_time_ms,
                user_input=user_input,
                agent_response=agent_response,
            ) from e

    async def process_audio_with_transcript(self, audio_bytes: bytes, **kwargs) -> Tuple[bytes, Dict, int]:
        """
        Process audio and capture transcript data.
        Returns: (response_audio, transcript_dict, processing_time_ms)
        """
        result = await self.process_audio(audio_bytes, **kwargs)
        transcript_dict = self._create_transcript_data(
            result.transcript.user_input, 
            result.transcript.agent_response
        )
        return result.audio_bytes, transcript_dict, result.processing_time_ms

    async def process_text_with_timing(self, text_input: str, **kwargs) -> Tuple[str, int]:
        """Process text and capture processing time."""
        start_time = time.perf_counter()
        agent_response, _ = await self.process_text(text_input, **kwargs)
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)
        return agent_response, processing_time_ms

    def _create_transcript_data(self, user_input: str, agent_response: str) -> Dict:
        """Create structured transcript data."""
        return {
            "user_input": user_input,
            "agent_response": agent_response
        }
    
    async def process_text(self, text_input: str, **kwargs) -> Tuple[str, bytes]:
        """Process a text query and return both text and synthesized audio."""
        if not self.is_initialized:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        
        try:
            self.logger.info(f"Processing text query: {text_input}")
            agent_response = await self.llm_agent.process_query(text_input, **kwargs)
            
            response_audio = await self.tts.synthesize(agent_response, **kwargs)
            
            return agent_response, response_audio
            
        except Exception as e:
            self.logger.error(f"Text processing failed: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, bool]:
        """Check the health status of all pipeline components."""
        return {
            "pipeline_initialized": self.is_initialized,
            "stt_ready": self.stt.is_ready() if self.stt else False,
            "llm_ready": self.llm_agent.is_initialized if self.llm_agent else False,
            "tts_ready": self.tts.is_ready() if self.tts else False,
        }
    
    async def cleanup(self) -> None:
        """Cleanup all pipeline resources."""
        self.logger.info("Cleaning up pipeline resources...")
        
        try:
            if self.stt:
                await self.stt.cleanup()
            if self.llm_agent:
                await self.llm_agent.cleanup()
            if self.tts:
                await self.tts.cleanup()
                
            self.stt = None
            self.llm_agent = None
            self.tts = None
            self.is_initialized = False
            
            self.logger.info("Pipeline cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
            raise


async def create_pipeline(
    stt_config: Dict[str, Any],
    llm_config: Dict[str, Any],
    tts_config: Dict[str, Any],
    enable_logging: bool = True
) -> AudioSupportPipeline:
    """Factory function to create and initialize a pipeline."""
    config = PipelineConfig(
        stt_config=stt_config,
        llm_config=llm_config,
        tts_config=tts_config,
        enable_logging=enable_logging
    )
    
    pipeline = AudioSupportPipeline(config)
    await pipeline.initialize()
    
    return pipeline


if __name__ == "__main__":
    """
    Example usage of the pipeline.
    Students can use this for testing their implementation.
    """
    async def main():
        stt_config = {
            "api_key": "your_openai_api_key",
            "model": "whisper-1"
        }
        
        llm_config = {
            "api_key": "your_openai_api_key",
            "model": "gpt-4o-mini",
            "temperature": 0.2,
            "memory_window": 6
        }
        
        tts_config = {
            "voice": "en-US-AriaNeural"
        }
        
        pipeline = await create_pipeline(stt_config, llm_config, tts_config)
        response_text, response_audio = await pipeline.process_text("What is your return policy?")
        print(f"Response: {response_text}")
        print(f"Generated audio bytes: {len(response_audio)}")
        await pipeline.cleanup()
    
    asyncio.run(main())