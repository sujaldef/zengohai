# Setup & Installation Guide

## System Requirements

- **Python**: 3.10 or later
- **OS**: Windows, macOS, or Linux
- **Optional**: FFmpeg (for non-WAV audio formats on Windows)

## Quick Start (5 minutes)

### 1. Clone and Navigate

```bash
cd audio_support_agent
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks execution, run once:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

**Windows (Command Prompt):**

```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and set your API keys:

```env
# Choose ONE provider:
# Option A: OpenAI (for both STT and LLM)
OPENAI_API_KEY=sk-...

# Option B: Groq (for LLM) + Local or OpenAI STT
GROQ_API_KEY=gsk-...

# Speech-to-Text Model
# Options: "whisper-1" (OpenAI API), "base", "small", "medium", "large" (local)
# Default: "base" (local)
STT_MODEL=base

# LLM Model
# OpenAI: "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"
# Groq: "llama2-70b-4096", "mixtral-8x7b-32768", "gemma-7b-it"
# Default: gpt-4o-mini
LLM_MODEL=gpt-4o-mini

# LLM Temperature (0.0-1.0)
# Lower = more deterministic, Higher = more creative
LLM_TEMPERATURE=0.2

# Text-to-Speech Voice
# Examples: "en-US-AriaNeural", "en-US-GuyNeural", "en-GB-SoniaNeural"
EDGE_TTS_VOICE=en-US-AriaNeural

# Session Memory Window
# Number of recent conversation turns to keep in memory (default: 6)
MEMORY_WINDOW=6

# Logging Level
LOG_LEVEL=INFO
```

## Environment Variables Reference

### LLM Provider Selection

The system automatically selects a provider based on configuration:

1. If `GROQ_API_KEY` is set → uses Groq for LLM
2. If `OPENAI_API_KEY` is set → uses OpenAI for LLM
3. To override, explicitly set `LLM_PROVIDER=openai` or `LLM_PROVIDER=groq`

### STT Configuration

- **`STT_MODEL=whisper-1`**: Use OpenAI Whisper API (requires `OPENAI_API_KEY`)
- **`STT_MODEL=base|small|medium|large`**: Use local OpenAI Whisper model (slower, no key needed)

### Audio Format Handling

- **WAV files**: Fully supported on Windows without external dependencies
- **MP3, FLAC, OGG**: Supported on macOS/Linux; on Windows requires FFmpeg
- **Recommended**: Upload WAV files for best compatibility

## Optional: Install FFmpeg (Windows)

If you want to support non-WAV audio formats on Windows:

### Using Chocolatey (Recommended)

```powershell
choco install ffmpeg
```

### Using Windows Package Manager

```cmd
winget install ffmpeg
```

### Manual Download

Download from https://ffmpeg.org/download.html and add to PATH.

## Verify Installation

```bash
# Test Python environment
python --version

# Test dependencies
python -c "import fastapi; import streamlit; import langchain; print('All imports successful')"

# Run tests
pytest -v

# Check API health
python -m src.api.server &
sleep 2
curl http://localhost:8000/health
```

## Troubleshooting

### `ModuleNotFoundError`

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### API won't start (503 Pipeline not initialized)

- Check `.env` file exists and has valid API keys
- Verify `OPENAI_API_KEY` or `GROQ_API_KEY` is set
- Check logs for specific initialization errors

### Audio upload fails with "FFmpeg missing"

- You uploaded a non-WAV format without FFmpeg installed
- Either install FFmpeg (see above) or use WAV format

### Streamlit connection refused

- Ensure FastAPI server is running (`python -m src.api.server`)
- Check port 8000 is not in use
- Verify `API_URL` in Streamlit matches your server address

### ChromaDB errors

- Delete `data/chroma_db` to reset the knowledge base
- Restart the server to rebuild it on startup

## Next Steps

- See **ASSIGNMENT_GUIDE.md** for architecture overview
- See **RUNNING.md** for how to start the application
- See **ARCHITECTURE_EXPLANATION.md** for detailed component descriptions
