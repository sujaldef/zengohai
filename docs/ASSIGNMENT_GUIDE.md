# Assignment Implementation Guide

## Project Overview

**Audio Customer Support Agent** is a production-oriented system that processes customer inquiries through a full audio pipeline:

```
Audio Input → STT (Whisper) → LLM + RAG (Groq/OpenAI + ChromaDB) → TTS (Edge-TTS) → Audio Output
```

The system includes mid-session memory and health monitoring.

## Assignment Requirements ✅

All assignment requirements have been implemented:

### 1. **Speech-to-Text (STT)** ✅

**File**: `src/stt/base_stt.py`

- ✅ Accepts raw audio bytes
- ✅ Supports OpenAI Whisper API (`model="whisper-1"`)
- ✅ Supports local Whisper models (`model="base"`, `"small"`, etc.)
- ✅ Async/await pattern
- ✅ Error handling for corrupt/empty audio
- ✅ Windows FFmpeg workaround for WAV files

**Test**: `tests/test_stt.py`

### 2. **Retrieval-Augmented Generation (RAG)** ✅

**File**: `src/llm/agent.py` (method: `_rag_search()`)

- ✅ ChromaDB integration for persistent knowledge base
- ✅ Sentence-Transformers embeddings (`all-MiniLM-L6-v2`)
- ✅ Query-time retrieval with top-k=3 results
- ✅ Metadata filtering and distance-based ranking
- ✅ Context injection into LLM prompt
- ✅ 16 pre-loaded customer support documents

**Verification**:

```bash
python src/utils/kb_test.py  # Verify knowledge base
```

### 3. **Large Language Model (LLM)** ✅

**File**: `src/llm/agent.py`

- ✅ OpenAI ChatGPT integration (models: `gpt-4o-mini`, `gpt-4`, etc.)
- ✅ Groq LLaMA integration (`llama2-70b-4096`, `mixtral-8x7b-32768`, etc.)
- ✅ Provider auto-selection (Groq if `GROQ_API_KEY` set, else OpenAI)
- ✅ Prompt engineering with RAG context and conversation history
- ✅ Token-aware response generation
- ✅ Async/await pattern

### 4. **Text-to-Speech (TTS)** ✅

**File**: `src/tts/base_tts.py`

- ✅ Edge-TTS synthesis engine
- ✅ MP3 output format
- ✅ Voice selection and customization
- ✅ Stream-based synthesis for large responses
- ✅ Available voice listing

### 5. **FastAPI Integration** ✅

**File**: `src/api/server.py`

Endpoints:

- ✅ `GET /` - Root welcome
- ✅ `GET /health` - Component health check
- ✅ `POST /chat/text` - Text input → text response
- ✅ `POST /chat/audio` - Audio file → audio response
- ✅ `GET /chat/audio/{text}` - Text → audio (TTS direct)
- ✅ `POST /debug/stt` - STT debugging endpoint
- ✅ CORS support for Streamlit
- ✅ Error handling and logging

### 6. **Streamlit Interface** ✅

**File**: `streamlit_app.py`

Tabs:

- ✅ **Text Chat**: Send text queries, see responses
- ✅ **Audio Chat**: Record/upload audio, get audio responses
- ✅ **Health Monitor**: View component status and metrics
- ✅ **Documentation**: Browse project docs

### 7. **Audio Pipeline** ✅

**File**: `src/pipeline.py`

- ✅ Orchestrates STT → LLM → TTS workflow
- ✅ Error handling and cleanup
- ✅ Health status reporting
- ✅ Async methods for all operations

### 8. **Mid-Session Memory** ✅

**File**: `src/llm/agent.py`

- ✅ `ConversationBufferMemory` from LangChain
- ✅ Configurable window size (default: 6 turns)
- ✅ Recent message retrieval for prompt context
- ✅ Clear on session reset

### 9. **Error Handling & Logging** ✅

**All files**:

- ✅ Try-catch blocks for all external service calls
- ✅ Structured logging with `logging` module
- ✅ Clear error messages in API responses
- ✅ HTTP status codes (400, 500, 503)

### 10. **Testing** ✅

**File**: `tests/test_stt.py`

- ✅ Unit tests for STT initialization
- ✅ Integration test markers (`@pytest.mark.integration`)
- ✅ All tests passing (9 passed, 1 skipped)
- ✅ Pytest configuration in `pytest.ini`

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                           │
│  ┌──────────────────────┐          ┌──────────────────────┐ │
│  │   Streamlit App      │          │   FastAPI Server     │ │
│  │  (Text/Audio Chat)   │◄────────►│  (Health, Endpoints) │ │
│  └──────────────────────┘          └──────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
    ┌─────────┐   ┌──────────┐   ┌─────────┐
    │   STT   │   │ Pipeline │   │   TTS   │
    │(Whisper)│   │Orchestr. │   │(Edge-TS)│
    └─────────┘   └──────────┘   └─────────┘
         │              │              │
         └──────────────┼──────────────┘
                        ▼
                   ┌──────────────┐
                   │   LLM Agent  │
                   └──────────────┘
                        │
         ┌──────────────┬──────────────┐
         ▼              ▼              ▼
    ┌─────────┐   ┌──────────┐   ┌──────────┐
    │  RAG    │   │ ChromaDB │   │  Memory  │
    │(Search) │   │(Knowledge)   │(Dialogue)│
    └─────────┘   └──────────┘   └──────────┘
```

## Key Implementation Details

### Provider Configuration

**Automatic Detection:**

```env
GROQ_API_KEY=xxx          # Uses Groq LLM
# OR
OPENAI_API_KEY=yyy        # Uses OpenAI LLM
```

**Explicit Override:**

```env
LLM_PROVIDER=groq         # Force Groq
LLM_PROVIDER=openai       # Force OpenAI
```

### STT Model Selection

```env
STT_MODEL=whisper-1       # OpenAI API (requires OPENAI_API_KEY)
STT_MODEL=base            # Local model (no key needed, ~140MB download)
STT_MODEL=small           # Local model (~500MB)
STT_MODEL=medium          # Local model (~1.4GB)
STT_MODEL=large           # Local model (~2.9GB)
```

### Knowledge Base

- **Storage**: `data/chroma_db/` (persistent)
- **Documents**: 16 customer support policies
- **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Retrieval**: Top-3 documents per query + distance ranking
- **Auto-load**: On first API startup

### Memory System

- **Type**: In-memory conversation buffer (session scope)
- **Window**: Configurable (default: 6 turns = 12 messages)
- **Context**: Recent messages injected into system prompt
- **Reset**: On server restart or explicit call

## Testing Coverage

```bash
# Run all tests
pytest -v

# Run only unit tests (skip integration tests)
pytest -v -m "not integration"

# Test specific component
pytest tests/test_stt.py -v

# Check knowledge base
python src/utils/kb_test.py
```

## Deployment Checklist

Before submission, verify:

- [ ] `.env` file exists with valid API key(s)
- [ ] `python -m src.api.server` starts without errors
- [ ] `GET /health` returns all components ready
- [ ] `POST /chat/text` with {"text": "test"} returns response
- [ ] `POST /chat/audio` with WAV file returns MP3
- [ ] `streamlit run streamlit_app.py` loads successfully
- [ ] Text chat works in Streamlit
- [ ] Audio chat works in Streamlit
- [ ] Health monitor shows component status
- [ ] `pytest` passes (9 passed, 1 skipped)

## Files & Modules

```
src/
├── __init__.py
├── pipeline.py              # Orchestration (STT → LLM → TTS)
├── stt/
│   ├── __init__.py
│   └── base_stt.py          # Whisper integration
├── llm/
│   ├── __init__.py
│   └── agent.py             # LLM + RAG + Memory
├── tts/
│   ├── __init__.py
│   └── base_tts.py          # Edge-TTS integration
├── api/
│   ├── __init__.py
│   └── server.py            # FastAPI server
└── utils/
    ├── __init__.py
    └── kb_test.py           # KB verification tool
```

## Troubleshooting

### API Won't Start

```bash
# Check environment
cat .env | grep OPENAI_API_KEY

# Restart with verbose logging
LOG_LEVEL=DEBUG python -m src.api.server
```

### STT Fails with FFmpeg Error

- Upload WAV files (no FFmpeg needed)
- Or install FFmpeg for other formats

### Memory Not Persisting

- Memory is **session-scoped** (in-process, not persistent)
- Restarting the server resets conversation history

### RAG Returns Empty Results

```bash
# Check knowledge base
python src/utils/kb_test.py

# If empty, reset and restart
rm -rf data/chroma_db/
python -m src.api.server
```

## Next Steps

- See **RUNNING.md** to start the application
- See **ARCHITECTURE_EXPLANATION.md** for detailed component design
- See **VIDEO_DEMO_SCRIPT.md** for demo talking points
