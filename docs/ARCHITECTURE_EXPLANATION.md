# Architecture Explanation

## System Design

This project is a modular audio customer support system built around a single request pipeline:

Audio Input -> STT -> LLM + RAG -> TTS -> Audio Output

The implementation is intentionally split into small services so each stage can be tested and replaced independently. The FastAPI server owns orchestration, while the Streamlit app provides a human-friendly way to exercise the API.

## Component Responsibilities

### STT Service

File: `src/stt/base_stt.py`

- Receives raw audio bytes.
- Converts speech to text using the OpenAI transcription API with a Whisper model.
- Validates initialization and input size.
- Returns plain text for downstream processing.

### LLM Agent

File: `src/llm/agent.py`

- Loads the customer support knowledge base from ChromaDB.
- Retrieves relevant support documents for each user query.
- Builds the final prompt with retrieved context and recent conversation history.
- Uses OpenAI chat completions to generate a grounded answer.
- Persists a lightweight session memory buffer for follow-up questions.

### TTS Service

File: `src/tts/base_tts.py`

- Receives a text response from the LLM.
- Synthesizes MP3 audio using Edge TTS.
- Returns audio bytes for the API and Streamlit UI.

### Pipeline

File: `src/pipeline.py`

- Initializes STT, LLM, and TTS.
- Runs audio through transcription, response generation, and synthesis.
- Exposes `process_audio()` and `process_text()` for API usage.
- Handles cleanup and health reporting.

### Audio Response Envelope

File: `src/api/server.py`

- Converts synthesized audio bytes to base64 for JSON transport.
- Returns the user transcript, agent response, and processing time alongside the audio payload.
- Uses a consistent error envelope so the frontend can display partial information when a stage fails.

### FastAPI Server

File: `src/api/server.py`

- Loads environment variables.
- Initializes the pipeline on startup.
- Exposes health, text chat, audio chat, TTS debug, and STT debug endpoints.
- Keeps the server running even if initialization fails, which makes debugging easier.

### Streamlit UI

File: `streamlit_app.py`

- Tests the API through a visual interface.
- Supports text chat, audio upload, recording, and component health monitoring.
- Serves as the fastest way to verify the end-to-end user experience.

## Pipeline Flow

1. A user speaks into the microphone or uploads an audio file.
2. The API server receives the audio and forwards it to the pipeline.
3. STT converts the audio to text.
4. The LLM agent searches ChromaDB for relevant support knowledge.
5. The retrieved context and short-term chat history are combined into a prompt.
6. The LLM generates a support response.
7. TTS converts the response to MP3 audio.
8. The pipeline measures processing time and returns transcript metadata plus audio bytes.
9. The API base64-encodes the audio and returns a structured JSON response to the client.

## RAG Explanation

The knowledge base is stored in ChromaDB and populated with 16 customer support documents covering returns, shipping, payments, warranty, account management, and technical support.

For each query:

- The agent queries ChromaDB with the user request.
- ChromaDB returns the top matching documents, metadata, and distances.
- The agent formats those results into readable context.
- The LLM uses that context to answer with support-specific grounding.

This keeps the assistant focused on the company policy content instead of hallucinating generic answers.

## Memory Implementation Explanation

The assistant uses a lightweight mid-session memory model.

- The conversation buffer stores recent user and assistant messages for the current server session.
- Before generating a response, the agent includes only the most recent turns in the prompt.
- This gives the assistant continuity for follow-up questions like "What about shipping?" or "How do I do that?".
- The memory is intentionally short-lived and in-process, which keeps it simple and predictable.

Why this approach:

- It is easy to understand and debug.
- It avoids the complexity of long-term user profiles.
- It works well for interactive support sessions where context only needs to survive across a few exchanges.

## Transcript and Timing Metadata

The updated audio flow now returns more than raw audio bytes.

- The STT output is captured as `transcript.user_input`.
- The LLM output is captured as `transcript.agent_response`.
- The full audio turn is measured in `processing_time_ms`.
- The API wraps those fields in a JSON response and base64-encodes the MP3 audio for client transport.

This gives the Streamlit UI enough structured data to display the transcript, show the answer text, and report latency without needing to infer anything from the audio payload itself.

## Scalability Discussion

This implementation is small and explainable, but it can scale with a few targeted changes:

- Replace in-process memory with Redis or another shared store to support multiple workers.
- Cache common ChromaDB retrieval results for repeated policy questions.
- Move audio jobs to a background queue if requests become expensive.
- Add authentication and per-user session IDs before exposing the service broadly.
- Add observability around STT latency, retrieval quality, and synthesis time.
- Add dashboards or logs around the new response timing metric for audio turns.
- Swap OpenAI or Edge TTS for local model deployments if cost or privacy becomes a concern.

The current design is a good baseline because the components are already separated. That makes it straightforward to upgrade one layer without rewriting the whole system.
