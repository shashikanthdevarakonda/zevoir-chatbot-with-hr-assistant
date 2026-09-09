import pickle
import faiss
import numpy as np
import requests
from difflib import SequenceMatcher

# =====================================================
# CONFIG
# =====================================================

FAISS_INDEX = "vectorstore/faiss_index.bin"
METADATA_FILE = "vectorstore/metadata.pkl"

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"

CHAT_MODEL = "llama3.2:3b"   


# =====================================================
# LOAD VECTOR STORE
# =====================================================

print("🔄 Loading Vector Store...")

index = faiss.read_index(FAISS_INDEX)

with open(METADATA_FILE, "rb") as f:
    metadata = pickle.load(f)

print(f"✅ Vector Store Loaded | {index.ntotal} chunks")


# =====================================================
# SPECIAL CASE HANDLER (NEW)
# =====================================================

def handle_special_cases(question):
    """Handle special questions that need specific responses"""
    
    question_lower = question.lower().strip()
    
    # Contact Support
    if "contact" in question_lower and "support" in question_lower:
        return {
            "reply": "📞 You can contact Zevoir Technologies support:\n\n"
                    "📧 Email: contactus@zevoirtechnologies.com.au\n"
                    "📍 Location: Sydney, NSW 2145, Australia\n"
                    "🌐 Website: zevoirtechnologies.com.au\n\n"
                    "Feel free to reach out with any queries about our AI services!",
            "sources": []
        }
    
    # Talk to Agent
    if "talk to" in question_lower or "speak to" in question_lower or "agent" in question_lower:
        return {
            "reply": "🤖 I'm Zevoir's AI Assistant, here to help answer questions about our services!\n\n"
                    "For direct communication with our team:\n\n"
                    "📧 Email: contactus@zevoirtechnologies.com.au\n"
                    "📍 Call or visit us in Sydney, NSW 2145, Australia\n\n"
                    "But first, feel free to ask me anything about our AI solutions, services, or capabilities!",
            "sources": []
        }
    
    # Tell me about yourself
    if "about yourself" in question_lower or "who are you" in question_lower or "what are you" in question_lower:
        return {
            "reply": "👋 I'm the Zevoir Technologies AI Assistant!\n\n"
                    "I'm here to help you learn about Zevoir's AI and technology solutions including:\n\n"
                    "✅ Chatbot Solutions\n"
                    "✅ AI Assistant Solutions\n"
                    "✅ AI Automation Agents\n"
                    "✅ Machine Learning Models\n"
                    "✅ Cloud Migration Services\n"
                    "✅ Data & Analytics\n"
                    "✅ Web & Mobile App Solutions\n"
                    "✅ Integration & API Services\n"
                    "✅ AI Governance & Security\n\n"
                    "Ask me anything about these services or how Zevoir can help your business!",
            "sources": []
        }
    
    return None


# =====================================================
# DOMAIN CHECK
# =====================================================



def is_zevoir_related(question):

    question = question.lower()

    keywords = [
        "zevoir",
        "service",
        "solution",
        "chatbot",
        "automation",
        "ai",
        "cloud",
        "mobile",
        "analytics",
        "integration",
        "api",
        "company"
    ]

    for word in question.split():
        for key in keywords:
            if SequenceMatcher(None, word, key).ratio() > 0.75:
                return True

    return False


# =====================================================
# EMBEDDING
# =====================================================

def get_embedding(text):

    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": "nomic-embed-text",
            "prompt": text
        }
    )

    return response.json()["embedding"]


# =====================================================
# RETRIEVE CHUNKS
# =====================================================

def retrieve_chunks(query, top_k=2):

    query_embedding = get_embedding(query)

    query_vector = np.array([query_embedding]).astype("float32")

    distances, indices = index.search(query_vector, top_k)

    results = []

    for i, distance in zip(indices[0], distances[0]):

        if i == -1:
            continue

        chunk = metadata[i]

        text = chunk.get("text", "").strip()

        if not text:
            continue

        print("Distance:", distance)
        results.append(chunk)

    print("Retrieved Context Preview:")

    for r in results:
        print(r.get("text", "")[:200])

    return results


# =====================================================
# GENERATE ANSWER
# =====================================================

def generate_answer(user_question, chunks):

    if not chunks:
        return {
            "reply": "I can only answer questions about Zevoir Technologies.",
            "sources": []
        }

    context = "\n\n".join(
        chunk.get("text", "")
        for chunk in chunks
    )

    prompt = f"""
Answer briefly using ONLY the context.

If not found:
"I can only answer questions about Zevoir Technologies."

Context:
{context}

Question:
{user_question}

Answer in 2-4 lines:
"""

    response = requests.post(
        OLLAMA_CHAT_URL,
        json={
            "model": CHAT_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a strict RAG assistant. Use only provided context."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 80
            }
        }
    )

    answer = response.json()["message"]["content"].strip()

    # =================================================
    # HARD SAFETY / LEAKAGE PROTECTION
    # =================================================

    bad_patterns = [
        "context:",
        "question:",
        "answer:",
        "rules:",
        "context",
    ]

    if any(p in answer.lower() for p in bad_patterns):
        answer = "I can only answer questions about Zevoir Technologies."

    # =================================================
    # SOURCES
    # =================================================

    unique_sources = {}

    for chunk in chunks:
        url = chunk.get("url")

        if url and url not in unique_sources:
            unique_sources[url] = {
                "title": chunk.get("title", "Untitled"),
                "url": url
            }

    sources = list(unique_sources.values())

    return {
        "reply": answer,
        "sources": sources
    }


# =====================================================
# MAIN FUNCTION
# =====================================================

def rag_query(question):

    print("QUESTION RECEIVED:", question)
    
    # STEP 1: CHECK SPECIAL CASES FIRST
    special_response = handle_special_cases(question)
    if special_response:
        print("SPECIAL CASE MATCHED")
        return special_response
    
    # STEP 2: PROCEED WITH NORMAL RAG
    print("DOMAIN CHECK:", is_zevoir_related(question))

    if not is_zevoir_related(question):
        return {
            "reply": "I can only answer questions about Zevoir Technologies.",
            "sources": []
        }

    chunks = retrieve_chunks(question)

    return generate_answer(question, chunks)