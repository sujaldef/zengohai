# Running the Application

## Starting the System

### Terminal 1: FastAPI Server

```bash
# From repo root
python -m src.api.server
```

Expected output:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

The server initializes:

1. Loads LLM provider (OpenAI or Groq)
2. Initializes STT model (local or API)
3. Loads ChromaDB knowledge base
4. Sets up TTS engine
5. Starts health monitoring

### Terminal 2: Streamlit UI (Optional)

In a new terminal:

```bash
streamlit run streamlit_app.py
```

Expected output:

```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://xxx.xxx.xxx.xxx:8501
```

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "healthy",
  "components": {
    "pipeline_initialized": true,
    "stt_ready": true,
    "llm_ready": true,
    "tts_ready": true
  },
  "message": "All components ready"
}
```

### Text Chat

```bash
curl -X POST http://localhost:8000/chat/text \
  -H "Content-Type: application/json" \
  -d '{"text": "What is your return policy?"}'
```

Response:

```json
{
  "response_text": "Our return policy is...",
  "audio_available": true,
  "processing_time_ms": 1234
}
```

### Audio Upload & Processing

```bash
curl -X POST http://localhost:8000/chat/audio \
  -F "audio=@recording.wav"
```

Returns MP3 audio directly (save as `.mp3`):

```bash
curl -X POST http://localhost:8000/chat/audio \
  -F "audio=@recording.wav" \
  --output response.mp3
```

### Text-to-Audio (Direct TTS)

```bash
curl -X GET "http://localhost:8000/chat/audio/What%20is%20shipping%20cost%3F" \
  --output tts_response.mp3
```

### STT Debug Endpoint

```bash
curl -X POST http://localhost:8000/debug/stt \
  -F "audio=@recording.wav"
```

Response:

```json
{
  "transcription": "What is your return policy?"
}
```

### API Documentation

Interactive docs at: `http://localhost:8000/docs`

## Streamlit Interface

### Tab 1: Text Chat

1. Enter a question (e.g., "What is your return policy?")
2. Click "Send"
3. View LLM response and audio availability indicator
4. Audio plays automatically if available

### Tab 2: Audio Chat

1. **Record Audio**: Click microphone button (requires microphone)
   - Or manually record and upload
2. **Upload Audio**: Click "Choose an audio file"
3. Click "Process"
4. View transcription and response
5. Audio response plays automatically

### Tab 3: Health Monitor

- Real-time component status
- API connectivity indicator
- Service latency metrics
- Refresh button

### Tab 4: Documentation

- Browse project docs
- Architecture diagrams
- API reference

## Example Workflow

### Scenario 1: Text Query

```bash
Terminal 1: python -m src.api.server
Terminal 2: streamlit run streamlit_app.py
Browser:   http://localhost:8501
           → Tab: "Text Chat"
           → Question: "What is your return policy?"
           → Response shows in chat, audio plays
```

### Scenario 2: Audio Query

```bash
Terminal 1: python -m src.api.server
Terminal 2: streamlit run streamlit_app.py
Browser:   http://localhost:8501
           → Tab: "Audio Chat"
           → Upload: record or select "shipping.wav"
           → Click "Process"
           → Transcription shows
           → Response plays
```

### Scenario 3: Direct API Testing

```bash
Terminal 1: python -m src.api.server
Terminal 2:
  curl -X POST http://localhost:8000/chat/text \
    -H "Content-Type: application/json" \
    -d '{"text": "How do I track my order?"}'
```

## Monitoring & Debugging

### Server Logs

```bash
# Verbose logging
LOG_LEVEL=DEBUG python -m src.api.server

# JSON structured logging (for production)
LOG_FORMAT=json python -m src.api.server
```

### Test Knowledge Base

Verify RAG is working:

```bash
python src/utils/kb_test.py
```

Output:

```
Knowledge Base Test Results
==============================
Total documents: 16
Embedding model: all-MiniLM-L6-v2

Sample retrieval test:
Query: "How do I return my order?"
Results:
  1. Return Policy (distance: 0.123)
  2. Shipping Information (distance: 0.456)
  3. Customer Support (distance: 0.789)
```

### Run Tests

```bash
# All tests
pytest -v

# Specific test
pytest tests/test_stt.py::test_initialization -v

# Integration tests only
pytest -v -m integration
```

### Reset Knowledge Base

```bash
# Delete cached embeddings
rm -rf data/chroma_db/

# Restart server (will regenerate on startup)
python -m src.api.server
```

## Common Workflows

### Development: Local Testing

```bash
# Terminal 1
python -m src.api.server

# Terminal 2 (test script)
python -c "
import requests
import json

# Test health
health = requests.get('http://localhost:8000/health').json()
print('Health:', health['status'])

# Test text chat
response = requests.post(
    'http://localhost:8000/chat/text',
    json={'text': 'What is your return policy?'}
).json()
print('Response:', response['response_text'][:100])
"
```

### Demo: Walk-Through

```bash
# 1. Start server
python -m src.api.server &

# 2. Wait 3 seconds for initialization
sleep 3

# 3. Open Streamlit
streamlit run streamlit_app.py

# 4. Browser opens - navigate to Text Chat tab
# 5. Enter: "What is your return policy?"
# 6. Explain the RAG retrieval and memory
```

### Production: Docker Deployment

```bash
# Build image
docker build -t audio-support-agent .

# Run container
docker run -e OPENAI_API_KEY=xxx \
  -e LLM_MODEL=gpt-4o-mini \
  -p 8000:8000 \
  audio-support-agent
```

## Troubleshooting

### Server won't start

```bash
# Check dependencies
pip install -r requirements.txt

# Check environment
cat .env | grep -E "OPENAI|GROQ"

# Check port availability
netstat -an | grep 8000

# Start with verbose logging
LOG_LEVEL=DEBUG python -m src.api.server
```

### Streamlit won't connect

```bash
# Verify server is running
curl http://localhost:8000/health

# Check Streamlit port (default 8501)
netstat -an | grep 8501

# Clear cache
rm -rf ~/.streamlit/
```

### Audio processing fails

```bash
# Check audio format
file recording.wav

# For non-WAV, check FFmpeg
ffmpeg -version

# For WAV, test directly
curl -X POST http://localhost:8000/debug/stt \
  -F "audio=@recording.wav"
```

### Response quality issues

- Check RAG results: `python src/utils/kb_test.py`
- Verify LLM model: Check `.env` → `LLM_MODEL`
- Adjust temperature: Lower for consistency, higher for variety
- Check recent context: Memory window may need adjustment

## Next Steps

- See **SETUP_GUIDE.md** for installation details
- See **ARCHITECTURE_EXPLANATION.md** for technical deep-dive
- See **VIDEO_DEMO_SCRIPT.md** for demo talking points
