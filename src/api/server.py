"""FastAPI server for the audio customer support agent."""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import base64
import asyncio
import logging
import os

from dotenv import load_dotenv

from src.pipeline import AudioSupportPipeline, create_pipeline, PipelineConfig, AudioPipelineError
from src.api.models import AudioChatErrorResponse, AudioChatSuccessResponse, TranscriptData, EnhancedTextResponse

load_dotenv()


class TextRequest(BaseModel):
    """Request model for text-based queries."""
    text: str
    parameters: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    components: Dict[str, bool]
    message: str


class TextResponse(BaseModel):
    """Response model for text queries."""
    response_text: str
    audio_available: bool
    processing_time_ms: int


def build_audio_error_response(message: str, processing_time_ms: int, user_input: Optional[str] = None, agent_response: Optional[str] = None) -> AudioChatErrorResponse:
    """Build a consistent error payload for audio chat requests."""
    return AudioChatErrorResponse(
        error=message,
        transcript=TranscriptData(user_input=user_input, agent_response=agent_response),
        processing_time_ms=processing_time_ms,
    )


app = FastAPI(
    title="Audio Customer Support Agent API",
    description="REST API for testing the STT -> LLM -> TTS pipeline",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance
pipeline: Optional[AudioSupportPipeline] = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _clean_env(name: str) -> Optional[str]:
    """Return a stripped env value or None when unset/empty."""
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _detect_llm_provider(model: str, explicit_provider: Optional[str], groq_key: Optional[str]) -> str:
    """Choose LLM provider from explicit override, keys, or model family."""
    if explicit_provider:
        provider = explicit_provider.strip().lower()
        if provider in {"groq", "openai"}:
            return provider

    model_name = (model or "").lower()
    if groq_key or any(token in model_name for token in ("llama", "mixtral", "gemma")):
        return "groq"
    return "openai"


@app.on_event("startup")
async def startup_event():
    """Initialize the pipeline on server startup."""
    global pipeline
    
    try:
        logger.info("Starting Audio Support Agent API server...")

        groq_api_key = _clean_env("GROQ_API_KEY")
        openai_api_key = _clean_env("OPENAI_API_KEY")
        llm_api_key = groq_api_key or openai_api_key or _clean_env("LLM_API_KEY")
        llm_model = _clean_env("LLM_MODEL") or "gpt-4o-mini"
        explicit_provider = _clean_env("LLM_PROVIDER")
        llm_provider = _detect_llm_provider(llm_model, explicit_provider, groq_api_key)

        if not llm_api_key:
            logger.warning("Neither GROQ_API_KEY nor OPENAI_API_KEY is set. The server will start, but requests will fail until one is configured.")
        elif llm_provider == "groq" and not groq_api_key:
            logger.warning("LLM provider resolved to Groq but GROQ_API_KEY is empty. Set GROQ_API_KEY to process requests.")
        elif llm_provider == "openai" and not openai_api_key:
            logger.warning("LLM provider resolved to OpenAI but OPENAI_API_KEY is empty. Set OPENAI_API_KEY to process requests.")

        stt_config = {
            "api_key": openai_api_key,
            "model": os.getenv("STT_MODEL", "base"),
            "timeout": 60,
        }
        
        llm_config = {
            "api_key": llm_api_key,
            "model": llm_model,
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.2")),
            "memory_window": int(os.getenv("MEMORY_WINDOW", "6")),
            "provider": llm_provider,
            "groq_api_key": groq_api_key,
        }
        
        tts_config = {
            "voice": os.getenv("EDGE_TTS_VOICE", "en-US-AriaNeural"),
            "rate": os.getenv("EDGE_TTS_RATE", "+0%"),
            "volume": os.getenv("EDGE_TTS_VOLUME", "+0%"),
            "pitch": os.getenv("EDGE_TTS_PITCH", "+0Hz"),
        }
        
        pipeline = await create_pipeline(stt_config, llm_config, tts_config)
        logger.info("Pipeline initialized successfully.")
        
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {str(e)}")
        pipeline = None


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup pipeline resources on server shutdown."""
    global pipeline
    
    if pipeline:
        logger.info("Shutting down pipeline...")
        await pipeline.cleanup()
        pipeline = None


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Audio Customer Support Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns the status of all pipeline components.
    """
    global pipeline
    
    if not pipeline:
        return HealthResponse(
            status="unhealthy",
            components={
                "pipeline_initialized": False,
                "stt_ready": False,
                "llm_ready": False,
                "tts_ready": False
            },
            message="Pipeline not initialized"
        )
    
    try:
        components = await pipeline.health_check()
        
        all_healthy = all(components.values())
        
        return HealthResponse(
            status="healthy" if all_healthy else "unhealthy",
            components=components,
            message="All components ready" if all_healthy else "Some components not ready"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="error",
            components={},
            message=f"Health check failed: {str(e)}"
        )


@app.post("/chat/text", response_model=EnhancedTextResponse)
async def chat_text(request: TextRequest):
    """
    Process text query through the LLM agent.
    
    This endpoint allows testing the LLM component without audio processing.
    """
    global pipeline
    
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        response_text, processing_time_ms = await pipeline.process_text_with_timing(
            request.text,
            **(request.parameters or {})
        )
        
        return EnhancedTextResponse(
            response_text=response_text,
            processing_time_ms=processing_time_ms
        )
        
    except Exception as e:
        logger.error(f"Text processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/audio", response_model=AudioChatSuccessResponse)
async def chat_audio(audio: UploadFile = File(...)):
    """Process an audio query through the complete pipeline."""
    global pipeline
    
    if not pipeline:
        error_response = build_audio_error_response(
            "Pipeline not initialized",
            processing_time_ms=0,
        )
        return JSONResponse(status_code=503, content=jsonable_encoder(error_response))
    
    try:
        audio_bytes = await audio.read()
        
        if len(audio_bytes) == 0:
            error_response = build_audio_error_response(
                "Empty audio file",
                processing_time_ms=0,
            )
            return JSONResponse(status_code=400, content=jsonable_encoder(error_response))
        
        response_audio, transcript_dict, processing_time_ms = await pipeline.process_audio_with_transcript(audio_bytes)
        encoded_audio = base64.b64encode(response_audio).decode("ascii")

        response = AudioChatSuccessResponse(
            success=True,
            audio_response=encoded_audio,
            transcript=TranscriptData(**transcript_dict),
            processing_time_ms=processing_time_ms,
        )
        return JSONResponse(status_code=200, content=jsonable_encoder(response))
        
    except HTTPException:
        raise
    except AudioPipelineError as e:
        logger.error("Audio pipeline error: %s", str(e))
        error_response = build_audio_error_response(
            str(e),
            processing_time_ms=e.processing_time_ms,
            user_input=e.user_input,
            agent_response=e.agent_response,
        )
        return JSONResponse(status_code=500, content=jsonable_encoder(error_response))
    except Exception as e:
        logger.error(f"Audio processing failed: {str(e)}")
        error_response = build_audio_error_response(
            str(e),
            processing_time_ms=0,
        )
        return JSONResponse(status_code=500, content=jsonable_encoder(error_response))


@app.get("/chat/audio/{text}")
async def text_to_audio(text: str):
    """Convert text to audio using the TTS component directly."""
    global pipeline
    
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        if not pipeline.tts:
            raise HTTPException(status_code=503, detail="TTS not available")

        audio_bytes = await pipeline.tts.synthesize(text)
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=tts_output.mp3"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug/stt")
async def debug_stt(audio: UploadFile = File(...)):
    """Debug endpoint for testing STT component independently."""
    global pipeline
    
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        audio_bytes = await audio.read()
        
        if not pipeline.stt:
            raise HTTPException(status_code=503, detail="STT not available")

        transcription = await pipeline.stt.transcribe(audio_bytes)
        
        return {"transcription": transcription}
        
    except Exception as e:
        logger.error(f"STT debug failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )