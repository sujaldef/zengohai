# Audio Customer Support Agent

A production-oriented audio-first customer support system with speech recognition, intelligent retrieval-augmented generation (RAG), and text-to-speech synthesis.

## 🎯 Overview

```
Audio Input → Speech-to-Text → LLM + RAG → Text-to-Speech → Audio Output
```

This system processes customer inquiries through a complete audio pipeline:

1. **Input**: Accept audio or text queries
2. **STT**: Transcribe audio to text using Whisper
3. **RAG**: Retrieve relevant support documents from ChromaDB
4. **LLM**: Generate accurate, context-aware responses
5. **Memory**: Maintain conversation context across turns
6. **TTS**: Synthesize responses back to audio
7. **Output**: Deliver structured JSON, transcript metadata, and playable audio responses

## ✨ Key Features

- 🎤 **Multi-format Audio Input**: WAV, MP3, FLAC, OGG support
- 🧠 **RAG with ChromaDB**: 16+ customer support documents with semantic search
- 🔄 **Dual LLM Support**: OpenAI GPT-4 or Groq LLaMA
- 💬 **Conversation Memory**: In-session context window (configurable)
- 📝 **Transcript Metadata**: Audio chat returns user transcript, agent response, and processing time
- 📊 **Health Monitoring**: Real-time component status
- 🚀 **REST API**: FastAPI with auto-docs
- 🎨 **Web UI**: Streamlit interface for testing
- 📦 **Production-Ready**: Modular, async, error-handling

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key OR Groq API key
- Optional: FFmpeg (for non-WAV audio on Windows)

### 1. Install

```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY or GROQ_API_KEY
```

### 3. Run

**Terminal 1 - Start API Server:**

```bash
python -m src.api.server
```

**Terminal 2 - Open Streamlit UI:**

```bash
streamlit run streamlit_app.py
```

Visit `http://localhost:8501` in your browser.

## 📖 Documentation

| Document                                                        | Purpose                                          |
| --------------------------------------------------------------- | ------------------------------------------------ |
| [SETUP_GUIDE.md](docs/SETUP_GUIDE.md)                           | Detailed installation & configuration            |
| [ASSIGNMENT_GUIDE.md](docs/ASSIGNMENT_GUIDE.md)                 | Assignment requirements & implementation details |
| [RUNNING.md](docs/RUNNING.md)                                   | How to run & API examples                        |
| [ARCHITECTURE_EXPLANATION.md](docs/ARCHITECTURE_EXPLANATION.md) | System design deep-dive                          |
| [VIDEO_DEMO_SCRIPT.md](docs/VIDEO_DEMO_SCRIPT.md)               | 5-minute demo talking points                     |
| [FINAL_PROJECT_REVIEW.md](docs/FINAL_PROJECT_REVIEW.md)         | Formal submission readiness audit                |

## 🏗️ Architecture

### Components

```
┌─────────────────────────────────────┐
│     FastAPI Server + Streamlit      │
└────────────────┬────────────────────┘
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
    ┌─────┐  ┌──────┐  ┌─────┐
    │ STT │  │ LLM  │  │ TTS │
    └─────┘  │ +    │  └─────┘
  (Whisper)  │ RAG  │  (Edge-TTS)
             └──────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
    ┌──────────┐    ┌──────────┐
    │ ChromaDB │    │  Memory  │
    │(Knowledge)    │(Dialogue)│
    └──────────┘    └──────────┘
```

### File Structure

```
src/
├── pipeline.py           # Orchestration
├── stt/base_stt.py       # Speech-to-text
├── llm/agent.py          # LLM + RAG + Memory
├── tts/base_tts.py       # Text-to-speech
├── api/server.py         # FastAPI server
└── utils/kb_test.py      # KB verification

docs/
├── SETUP_GUIDE.md
├── ASSIGNMENT_GUIDE.md
├── RUNNING.md
├── ARCHITECTURE_EXPLANATION.md
└── FINAL_PROJECT_REVIEW.md

streamlit_app.py         # Web UI
tests/test_stt.py        # Test suite
requirements.txt         # Dependencies
.env.example            # Configuration template
```

## 🔌 API Endpoints

| Endpoint             | Method | Purpose                                                     |
| -------------------- | ------ | ----------------------------------------------------------- |
| `/`                  | GET    | Welcome message                                             |
| `/health`            | GET    | Component status                                            |
| `/chat/text`         | POST   | Process text query                                          |
| `/chat/audio`        | POST   | Process audio file and return JSON transcript/audio payload |
| `/chat/audio/{text}` | GET    | Direct text-to-audio                                        |
| `/debug/stt`         | POST   | Debug STT endpoint                                          |
| `/docs`              | GET    | Interactive API docs                                        |

**Example**:

```bash
curl -X POST http://localhost:8000/chat/text \
  -H "Content-Type: application/json" \
  -d '{"text": "What is your return policy?"}'
```

## 💾 Configuration

### Required

```env
# Choose ONE provider:
OPENAI_API_KEY=sk-...           # For OpenAI LLM
# OR
GROQ_API_KEY=gsk-...            # For Groq LLM
```

### Optional

```env
LLM_MODEL=gpt-4o-mini           # OpenAI or Groq model
STT_MODEL=base                  # Local whisper or "whisper-1" for API
EDGE_TTS_VOICE=en-US-AriaNeural # TTS voice
MEMORY_WINDOW=6                 # Conversation history turns
LOG_LEVEL=INFO                  # Logging verbosity
```

See [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for complete reference.

## ✅ Verification

### Check Knowledge Base

```bash
python src/utils/kb_test.py
```

### Verify Health and API Flow

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat/text \
  -H "Content-Type: application/json" \
  -d '{"text": "What is your return policy?"}'
```

## 🎤 Demo

1. Start the API server and Streamlit UI
2. Ask a text question (e.g., "What is your return policy?")
3. Upload an audio file or record a question
4. Show the Streamlit interface and health monitor
5. Explain the RAG retrieval, memory, transcript metadata, and processing timing

See [VIDEO_DEMO_SCRIPT.md](VIDEO_DEMO_SCRIPT.md) for detailed demo talking points.

## 📊 Requirements Met

- ✅ Speech-to-text (Whisper via OpenAI or local)
- ✅ Retrieval-augmented generation (ChromaDB + Sentence-Transformers)
- ✅ Large language model (OpenAI GPT-4o-mini or Groq LLaMA)
- ✅ Text-to-speech (Edge-TTS)
- ✅ FastAPI server with endpoints
- ✅ Streamlit web interface
- ✅ Audio pipeline orchestration
- ✅ Mid-session conversation memory
- ✅ Health monitoring
- ✅ Error handling & logging
- ✅ Structured audio transcript responses

## 🚨 Troubleshooting

### API won't start

```bash
# Check environment file
cat .env | grep -E "OPENAI|GROQ"

# Enable debug logging
LOG_LEVEL=DEBUG python -m src.api.server
```

### Audio processing fails

- Ensure audio is WAV format (or install FFmpeg for other formats)
- Test with: `curl -X POST http://localhost:8000/debug/stt -F "audio=@file.wav"`

### Streamlit won't connect

- Verify API is running: `curl http://localhost:8000/health`
- Check port 8501 is available: `netstat -an | grep 8501`

See [RUNNING.md](docs/RUNNING.md) for more troubleshooting.

## 📝 License

MIT

## 👤 Support

For issues or questions:

1. Check the [SETUP_GUIDE.md](docs/SETUP_GUIDE.md)
2. Review [ARCHITECTURE_EXPLANATION.md](docs/ARCHITECTURE_EXPLANATION.md)
3. See troubleshooting in [RUNNING.md](docs/RUNNING.md)
4. Check server logs: `LOG_LEVEL=DEBUG python -m src.api.server`

---

**Last Updated**: May 7, 2026  
**Status**: ✅ Production Ready for Submission
