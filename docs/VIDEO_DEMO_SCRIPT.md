# 5-Minute Demo Script

## 0:00 - 0:30 Opening

"Today I’m demonstrating an audio customer support agent built as a modular pipeline. The system takes audio input, transcribes it with Whisper, retrieves company policy context from ChromaDB, generates a grounded answer with OpenAI, and speaks the response back with Edge TTS. It also keeps a short conversation memory so follow-up questions stay in context. The audio endpoint now returns structured JSON with transcript metadata and processing time, so the UI can show the full interaction, not just the audio file."

## 0:30 - 1:15 Architecture Overview

"The architecture is split into four main services: STT, LLM plus RAG, TTS, and an orchestration pipeline. The FastAPI server exposes the endpoints, and the Streamlit app gives a visual interface for testing text chat, audio chat, and component health. This separation keeps the codebase modular and easy to test."

## 1:15 - 2:00 STT and TTS

"For speech-to-text, I use the OpenAI transcription API with Whisper. That means the system can accept uploaded audio or recorded audio and turn it into text reliably. On the output side, Edge TTS converts the final answer into MP3 audio, and the API returns that audio as base64 inside a structured JSON response together with the user transcript, the agent response, and the total processing time. The Streamlit app decodes that payload and plays the audio directly."

## 2:00 - 3:00 RAG and Memory

"The knowledge base lives in ChromaDB and contains the customer support policies. When the user asks a question, the agent retrieves the most relevant documents and injects them into the prompt. That keeps answers grounded in the actual support content. I also added lightweight mid-session memory, so if the user asks a follow-up question, the assistant can use the recent conversation history instead of starting from scratch."

## 3:00 - 4:30 Live Demo Walkthrough

"First I start the FastAPI server and confirm the health endpoint is ready. Then I open the Streamlit app. In the Text Chat tab, I ask a question like 'What is your return policy?' and show the response. Next, I switch to the Audio Chat tab, upload or record a short audio clip, and show that the system returns the transcript, the agent answer, the processing time, and an audio player from a single structured response. Finally, I open the Health Monitor tab to show that the API, STT, LLM, and TTS components are reporting correctly."

## 4:30 - 5:00 Close

"To summarize, this project demonstrates an end-to-end audio support workflow with STT, RAG, memory, and TTS, built in a way that is modular and production-oriented. The implementation is simple enough to explain, but structured so it can scale as new services or storage layers are added. The mid-session enhancement also makes the audio path more observable by returning transcript data and processing metrics alongside the synthesized audio."

## Demo Tips

- Keep the audio clip short, around 3 to 5 seconds.
- Use one obvious support question, such as returns or shipping.
- Show the health endpoint before the live chat.
- Keep the browser and terminal visible so the architecture feels real, not staged.
- If the network is slow, pre-run one text query so the UI loads a completed example.
