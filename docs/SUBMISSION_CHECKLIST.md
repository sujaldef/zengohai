# Submission Checklist

## Final Testing Checklist

- [ ] Virtual environment exists at `.venv`
- [ ] Dependencies install successfully with `python -m pip install -r requirements.txt`
- [ ] `OPENAI_API_KEY` is set in `.env`
- [ ] `python -m src.api.server` starts without syntax errors
- [ ] `GET /health` returns healthy or clearly explains missing configuration
- [ ] `POST /chat/text` returns a text response
- [ ] `POST /chat/audio` returns playable MP3 audio
- [ ] `GET /chat/audio/{text}` returns playable MP3 audio
- [ ] `POST /debug/stt` returns a transcription
- [ ] `streamlit run streamlit_app.py` opens successfully
- [ ] Text Chat works in Streamlit
- [ ] Audio Chat works in Streamlit
- [ ] Health Monitor shows component status
- [ ] `python src/utils/kb_test.py` runs successfully
- [ ] `pytest` runs successfully or known test gaps are documented

## Files to Upload

- [ ] `README.md`
- [ ] `ARCHITECTURE_EXPLANATION.md`
- [ ] `VIDEO_DEMO_SCRIPT.md`
- [ ] `SUBMISSION_CHECKLIST.md`
- [ ] Updated `src/llm/agent.py`
- [ ] Updated `src/stt/base_stt.py`
- [ ] Updated `src/tts/base_tts.py`
- [ ] Updated `src/pipeline.py`
- [ ] Updated `src/api/server.py`
- [ ] Updated `requirements.txt`

## Video Checklist

- [ ] Show the project name and one-sentence summary
- [ ] Explain the audio pipeline clearly
- [ ] Show STT, RAG, and TTS in the architecture
- [ ] Explain the mid-session memory feature
- [ ] Demonstrate one text query
- [ ] Demonstrate one audio query
- [ ] Show the health endpoint or health monitor
- [ ] Keep the demo under 5 minutes
- [ ] Speak clearly and avoid over-explaining internals

## Deployment / Run Verification

- [ ] `.env` is present and configured
- [ ] The API server runs from the repo root
- [ ] The Streamlit app connects to the API server
- [ ] The chosen OpenAI model responds to chat requests
- [ ] Whisper transcription works for uploaded audio
- [ ] Edge TTS generates an MP3 response
- [ ] Recent conversation context is preserved across multiple turns
- [ ] Knowledge base results come from ChromaDB, not hardcoded text

## Notes

- If the environment is fresh, re-run the dependency install before final testing.
- If audio playback fails, confirm the response is returned as `audio/mpeg`.
- If the server starts without a healthy status, check `.env` and the OpenAI API key first.
