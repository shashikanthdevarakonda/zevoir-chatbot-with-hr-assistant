"""
HR Assistant - RAG Engine
=========================
Assignment: RAG Chatbot for Email & WhatsApp Assistance.

Answers questions, drafts emails, and drafts WhatsApp messages using
ONLY the documents in hr_assistant/knowledge_base/ (Leave Policy, WFH
Policy, Holiday Calendar, HR Guidelines, Employee Handbook).

This module is fully independent of the existing rag.py / vectorstore/
used by the main Zevoir website chatbot — it has its own FAISS index
(vectorstore_hr/) and its own Ollama calls, so the original chatbot
is not touched or affected in any way.
"""

import os
import pickle
import re
from difflib import SequenceMatcher

import faiss
import numpy as np
import requests

# =====================================================
# CONFIG
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX = os.path.join(BASE_DIR, "vectorstore_hr", "hr_faiss_index.bin")
METADATA_FILE = os.path.join(BASE_DIR, "vectorstore_hr", "hr_metadata.pkl")

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"

EMBEDDING_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3.2:3b"

TOP_K = 3
# Optional FAISS L2 distance cutoff — chunks farther than this are treated as
# "not relevant" and short-circuit straight to the fallback message, skipping
# the LLM call. Left as None by default because the right cutoff value depends
# on your embedding model/dimension and is easiest to pick after watching a
# few real distances printed to the console (see retrieve_chunks below).
# To enable: set e.g. DISTANCE_THRESHOLD = 350.0 once you've observed typical
# "relevant" vs "irrelevant" distances for nomic-embed-text on your machine.
# With this left disabled, hallucination prevention still works via the LLM
# prompt instruction + the _sanitize() leakage/emptiness check below — the
# same approach already used by the main rag.py for the website chatbot.
DISTANCE_THRESHOLD = None

NOT_FOUND_MSG = "I couldn't find this information in the uploaded documents."

# =====================================================
# LOAD VECTOR STORE (lazy / safe)
# =====================================================

_index = None
_metadata = None
_load_error = None

try:
    if os.path.exists(FAISS_INDEX) and os.path.exists(METADATA_FILE):
        _index = faiss.read_index(FAISS_INDEX)
        with open(METADATA_FILE, "rb") as f:
            _metadata = pickle.load(f)
        print(f"HR Assistant: vectorstore loaded ({_index.ntotal} chunks)")
    else:
        _load_error = (
            "HR vectorstore not found. Run 'python hr_assistant/hr_ingestion.py' "
            "first to build it from the knowledge_base documents."
        )
        print(f"HR Assistant: {_load_error}")
except Exception as e:
    _load_error = f"Failed to load HR vectorstore: {e}"
    print(f"HR Assistant: {_load_error}")


# =====================================================
# EMBEDDING
# =====================================================

def get_embedding(text):
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={"model": EMBEDDING_MODEL, "prompt": text},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["embedding"]


# =====================================================
# RETRIEVAL
# =====================================================

def retrieve_chunks(query, top_k=TOP_K):
    """Returns (chunks, best_distance). chunks is [] if the store isn't loaded."""
    if _index is None or _metadata is None:
        return [], None

    query_embedding = get_embedding(query)
    query_vector = np.array([query_embedding]).astype("float32")

    distances, indices = _index.search(query_vector, top_k)

    results = []
    best_distance = None
    for idx, distance in zip(indices[0], distances[0]):
        if idx == -1:
            continue
        chunk = _metadata[idx]
        text = chunk.get("text", "").strip()
        if not text:
            continue
        results.append(chunk)
        if best_distance is None or distance < best_distance:
            best_distance = float(distance)

    print(f"HR Assistant | query='{query}' | best_distance={best_distance}")
    return results, best_distance


def _is_relevant(chunks, best_distance):
    if not chunks:
        return False
    if DISTANCE_THRESHOLD is not None and best_distance is not None and best_distance > DISTANCE_THRESHOLD:
        return False
    return True


def _build_context(chunks):
    return "\n\n".join(chunk.get("text", "") for chunk in chunks)


def _sources(chunks):
    seen = {}
    for chunk in chunks:
        src = chunk.get("source")
        if src and src not in seen:
            seen[src] = {"title": chunk.get("title", "Untitled"), "source": src}
    return list(seen.values())


# =====================================================
# HARD SAFETY / LEAKAGE FILTER (mirrors main rag.py's approach)
# =====================================================

_LEAK_PATTERNS = ["context:", "employee request:", "rules:", "as an ai", "policy context:"]


def _sanitize(answer):
    lowered = answer.lower()
    if any(p in lowered for p in _LEAK_PATTERNS):
        return NOT_FOUND_MSG
    if not answer.strip():
        return NOT_FOUND_MSG
    return answer.strip()


def _call_llm(system_prompt, user_prompt, num_predict=220):
    response = requests.post(
        OLLAMA_CHAT_URL,
        json={
            "model": CHAT_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": num_predict},
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["message"]["content"].strip()


# =====================================================
# 1. DOCUMENT-BASED Q&A
# =====================================================

def answer_question(question):
    if _index is None:
        return {"reply": _load_error or NOT_FOUND_MSG, "sources": []}

    chunks, best_distance = retrieve_chunks(question)

    if not _is_relevant(chunks, best_distance):
        return {"reply": NOT_FOUND_MSG, "sources": []}

    context = _build_context(chunks)

    prompt = f"""Answer the employee's question using ONLY the company policy context below.
Be concise and specific (include exact numbers/dates from the context where relevant).

If the answer is not contained in the context, respond with exactly:
"{NOT_FOUND_MSG}"

Context:
{context}

Question:
{question}

Answer:"""

    answer = _call_llm(
        "You are a strict HR policy assistant. You must never answer using information "
        "that is not present in the provided context.",
        prompt,
        num_predict=120,
    )

    answer = _sanitize(answer)
    return {"reply": answer, "sources": _sources(chunks) if answer != NOT_FOUND_MSG else []}


# =====================================================
# 2. EMAIL GENERATION
# =====================================================

def generate_email(request_text):
    if _index is None:
        return {"reply": _load_error or NOT_FOUND_MSG, "sources": []}

    chunks, best_distance = retrieve_chunks(request_text, top_k=4)

    if not _is_relevant(chunks, best_distance):
        return {"reply": NOT_FOUND_MSG, "sources": []}

    context = _build_context(chunks)

    prompt = f"""Draft a professional email for the employee's request below, using ONLY the
company policy context provided. Do not invent leave balances, dates, approvals, or any
policy detail that is not explicitly stated in the context.

If the context does not contain enough information to write an accurate email, respond
with exactly: "{NOT_FOUND_MSG}"

Format the email with a "Subject:" line, a greeting, a short professional body, and a
polite sign-off (e.g. "Regards,").

Company Policy Context:
{context}

Employee's Request:
{request_text}

Email:"""

    answer = _call_llm(
        "You are an HR communications assistant. You only use facts from the given "
        "context and never fabricate policy details, numbers, or dates.",
        prompt,
        num_predict=260,
    )

    answer = _sanitize(answer)
    return {"reply": answer, "sources": _sources(chunks) if answer != NOT_FOUND_MSG else []}


# =====================================================
# 3. WHATSAPP MESSAGE GENERATION
# =====================================================

def generate_whatsapp(request_text):
    if _index is None:
        return {"reply": _load_error or NOT_FOUND_MSG, "sources": []}

    chunks, best_distance = retrieve_chunks(request_text, top_k=3)

    if not _is_relevant(chunks, best_distance):
        return {"reply": NOT_FOUND_MSG, "sources": []}

    context = _build_context(chunks)

    prompt = f"""Draft a short, polite WhatsApp message for the employee's request below,
using ONLY the company policy context provided. Do not invent policy details, dates, or
approvals that are not in the context.

If the context does not contain enough information, respond with exactly: "{NOT_FOUND_MSG}"

Keep it to 2-4 short sentences, conversational, no subject line, no formal letter formatting.

Company Policy Context:
{context}

Employee's Request:
{request_text}

WhatsApp message:"""

    answer = _call_llm(
        "You are an HR communications assistant drafting brief WhatsApp messages. "
        "You only use facts from the given context and never fabricate details.",
        prompt,
        num_predict=120,
    )

    answer = _sanitize(answer)
    return {"reply": answer, "sources": _sources(chunks) if answer != NOT_FOUND_MSG else []}


# =====================================================
# EXTRACT EMAIL / PHONE NUMBER FROM THE MESSAGE
# =====================================================

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(?:\+?\d[\d\-\s]{8,14}\d)")


def extract_email(text):
    match = _EMAIL_RE.search(text)
    return match.group(0) if match else None


def extract_phone(text):
    match = _PHONE_RE.search(text)
    if not match:
        return None
    digits = re.sub(r"\D", "", match.group(0))
    return digits if len(digits) >= 10 else None


_WRAPPER_PATTERNS = [
    r"\bcan you\b", r"\bcould you\b", r"\bplease\b", r"\bkindly\b",
    r"\bsend\b", r"\bshare\b", r"\bprovide\b", r"\bforward\b",
    r"\bto my (whatsapp\s*)?(number|email|mail)\b",
    r"\bon my (whatsapp\s*)?(number|email|mail)\b",
    r"\bvia (whatsapp|email|mail)\b",
    r"\bwhatsapp message\b", r"\bwhatsapp\b", r"\be-?mail\b", r"\bmail\b",
]


def _strip_delivery_wrapper(text):
    """Removes the email/phone token and delivery phrasing ('send ... to my
    email/whatsapp ...') so retrieval and the LLM see just the actual topic,
    e.g. 'sick leave data' instead of the whole request sentence."""
    cleaned = _EMAIL_RE.sub(" ", text)
    cleaned = _PHONE_RE.sub(" ", cleaned)
    for pattern in _WRAPPER_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if cleaned else text


# =====================================================
# INTENT ROUTING
# =====================================================

def classify_intent(message):
    lower = message.lower()

    whatsapp_keywords = ["whatsapp", "wtsapp", "wattsapp", "whats app"]
    email_keywords = ["email", "e-mail", "mail to", "send a mail", "write a mail", "mail"]

    has_email_addr = extract_email(message) is not None
    has_phone = extract_phone(message) is not None
    mentions_whatsapp = any(k in lower for k in whatsapp_keywords)
    mentions_email = any(k in lower for k in email_keywords)

    # "send/mail the <policy info> to my email <address>" -> fetch the info and
    # confirm delivery, rather than drafting an email for someone else to read.
    if has_email_addr and mentions_email:
        return "deliver_email"

    # "send the <policy info> to my whatsapp number <number>" -> same idea for WhatsApp.
    if mentions_whatsapp and has_phone:
        return "deliver_whatsapp"

    if mentions_whatsapp:
        return "whatsapp"
    if mentions_email:
        return "email"
    return "qa"


# =====================================================
# "DELIVER TO ME" — fetch the answer, confirm it was sent
# =====================================================

def deliver_to_email(request_text, email_address):
    topic = _strip_delivery_wrapper(request_text)
    qa_result = answer_question(topic)
    if qa_result["reply"] == NOT_FOUND_MSG:
        return qa_result

    from hr_assistant.notifier import send_real_email

    subject = f"HR Info: {topic.title()}"
    formatted_body = (
        f"Dear User,\n\n"
        f"{qa_result['reply']}\n\n"
        f"Regards,\n"
        f"HR Team"
    )
    sent, status_msg = send_real_email(email_address, subject, formatted_body)

    if sent:
        reply = f"✅ Email actually sent to {email_address}:\n\n{qa_result['reply']}"
    else:
        reply = (
            f"⚠️ Could not actually send the email ({status_msg}).\n\n"
            f"Here's the information anyway:\n\n{qa_result['reply']}"
        )
    return {"reply": reply, "sources": qa_result["sources"]}


def deliver_to_whatsapp(request_text, phone_number):
    topic = _strip_delivery_wrapper(request_text)
    qa_result = answer_question(topic)
    if qa_result["reply"] == NOT_FOUND_MSG:
        return qa_result

    from hr_assistant.notifier import send_real_whatsapp

    formatted_body = (
        f"Hello User,\n\n"
        f"{qa_result['reply']}\n\n"
        f"- HR Team"
    )
    sent, status_msg = send_real_whatsapp(phone_number, formatted_body)

    if sent:
        reply = f"✅ WhatsApp message actually sent to {phone_number}:\n\n{qa_result['reply']}"
    else:
        reply = (
            f"⚠️ Could not actually send the WhatsApp message ({status_msg}).\n\n"
            f"Here's the information anyway:\n\n{qa_result['reply']}"
        )
    return {"reply": reply, "sources": qa_result["sources"]}


# =====================================================
# DOMAIN CHECK (used to route the shared website widget)
# =====================================================

_HR_KEYWORDS = [
    "leave", "leaves", "casual", "sick", "earned", "privilege",
    "wfh", "home", "holiday", "holidays", "calendar",
    "hr", "policy", "guidelines", "handbook",
    "notice", "resign", "resignation", "probation",
    "dress", "code", "attendance", "manager", "late",
    "email", "mail", "whatsapp", "message",
    "salary", "bonus", "harassment", "conduct",
]


def is_hr_related(question):
    """Fuzzy keyword match, mirroring is_zevoir_related() in the main rag.py,
    used to decide whether a message typed into the shared website widget
    should be routed to the HR assistant instead of the Zevoir services RAG."""
    question = question.lower()
    for word in question.split():
        for key in _HR_KEYWORDS:
            if SequenceMatcher(None, word, key).ratio() > 0.8:
                return True
    return False


def hr_rag_query(message):
    """Main entry point used by hr_routes.py and the shared website widget."""
    message = (message or "").strip()
    if not message:
        return {"reply": "Please type a question or request.", "sources": []}

    intent = classify_intent(message)

    if intent == "deliver_email":
        return deliver_to_email(message, extract_email(message))
    if intent == "deliver_whatsapp":
        return deliver_to_whatsapp(message, extract_phone(message))
    if intent == "email":
        return generate_email(message)
    if intent == "whatsapp":
        return generate_whatsapp(message)
    return answer_question(message)
