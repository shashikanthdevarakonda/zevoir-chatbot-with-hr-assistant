# HR Assistant Add-On (Assignment: RAG Chatbot for Email & WhatsApp Assistance)

This folder is a **self-contained add-on** to the existing Zevoir chatbot project.
It does not modify the original `rag.py`, `ingestion.py`, `vectorstore/`, or any
existing HTML/route — it only adds:

- 2 lines added to `app.py` (import + `register_blueprint`) so the new routes are live.
- Everything else lives inside this `hr_assistant/` folder.

## What it does

1. **Document-based Q&A** — answers questions using only the 5 HR documents in
   `knowledge_base/` (Leave Policy, WFH Policy, Holiday Calendar, HR Guidelines,
   Employee Handbook). Unsupported questions get:
   `"I couldn't find this information in the uploaded documents."`
2. **Email generation** — drafts a professional email grounded in the retrieved policy.
3. **WhatsApp message generation** — drafts a short, concise message grounded in policy.
4. **Hallucination prevention** — the model is instructed to only use retrieved
   context and to return the exact fallback line otherwise; a `_sanitize()` check
   also strips out any accidental prompt/context leakage.

## Setup

Make sure Ollama is running with the same models the main chatbot already uses
(`nomic-embed-text` for embeddings, `llama3.2:3b` for chat) — no new models or
Python packages are required; everything here reuses what's already in
`requirements.txt`.

1. Build the HR vectorstore (run once, and again whenever a `.txt` file in
   `knowledge_base/` changes):
   ```
   python hr_assistant/hr_ingestion.py
   ```
   This creates `hr_assistant/vectorstore_hr/hr_faiss_index.bin` and `hr_metadata.pkl`
   — completely separate from the main site's `vectorstore/`.

2. Run the app as usual:
   ```
   python app.py
   ```

3. Open the test chat UI:
   ```
   http://localhost:5000/hr-assistant
   ```

## API endpoints (for the test cases in the assignment)

- `POST /hr/chat` — send `{"message": "..."}`, auto-detects intent (Q&A / email / WhatsApp).
- `POST /hr/ask` — force Q&A mode.
- `POST /hr/generate-email` — force email drafting.
- `POST /hr/generate-whatsapp` — force WhatsApp drafting.

All return `{"reply": "...", "sources": [...]}`.

## Tuning

`hr_rag.py` prints the FAISS distance for every query
(`HR Assistant | query='...' | best_distance=...`). After running a few real
questions through Ollama, you can optionally set `DISTANCE_THRESHOLD` (top of
`hr_rag.py`) to a number to hard-cut off clearly irrelevant retrievals before
they even reach the LLM. It's left disabled by default since the right value
depends on your embedding model.

## Extending the knowledge base

Add/replace `.txt` files in `knowledge_base/` and re-run `hr_ingestion.py`.
No code changes needed to add more policy documents.
