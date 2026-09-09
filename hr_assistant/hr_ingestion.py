"""
HR Assistant - Ingestion Script
===============================
Builds a SEPARATE FAISS vectorstore from the HR knowledge base documents
(Leave Policy, WFH Policy, Holiday Calendar, HR Guidelines, Employee Handbook).

This is fully independent of the existing Zevoir website vectorstore
(vectorstore/faiss_index.bin, vectorstore/metadata.pkl) — it reads/writes
only inside hr_assistant/, so the original chatbot's data is untouched.

Run once (and again any time a knowledge base document changes):
    cd hr_assistant
    python hr_ingestion.py
"""

import os
import sys
import pickle

try:
    import faiss
    import numpy as np
    import ollama
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install faiss-cpu numpy ollama")
    sys.exit(1)

# -----------------------------------------------
# CONFIG
# -----------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vectorstore_hr")

EMBEDDING_MODEL = "nomic-embed-text"
CHUNK_SIZE = 120     # words per chunk (policy docs are short, so smaller chunks keep answers precise)
CHUNK_OVERLAP = 20   # word overlap between chunks

os.makedirs(VECTOR_STORE_DIR, exist_ok=True)


# -----------------------------------------------
# LOAD DOCUMENTS
# -----------------------------------------------
def load_documents():
    docs = {}
    if not os.path.isdir(KB_DIR):
        print(f"Knowledge base folder not found: {KB_DIR}")
        return docs

    for filename in sorted(os.listdir(KB_DIR)):
        if filename.lower().endswith(".txt"):
            path = os.path.join(KB_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()
            if text:
                title = filename.replace(".txt", "").replace("_", " ").title()
                docs[filename] = (text, title)
    return docs


# -----------------------------------------------
# CHUNKING
# -----------------------------------------------
def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    step = max(chunk_size - overlap, 1)

    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.split()) >= 8:  # keep even short policy snippets (e.g. leave counts)
            chunks.append(chunk)

    return chunks


# -----------------------------------------------
# EMBEDDING
# -----------------------------------------------
def create_embeddings(texts):
    embeddings = []
    for i, text in enumerate(texts):
        print(f"   Embedding {i + 1}/{len(texts)}...", end="\r")
        try:
            response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
            embeddings.append(response["embedding"])
        except Exception as e:
            print(f"\n   Warning: failed to embed chunk {i + 1}: {e}")
            embeddings.append([0.0] * 768)  # nomic-embed-text dimension fallback
    print()
    return embeddings


# -----------------------------------------------
# BUILD VECTORSTORE
# -----------------------------------------------
def build_hr_vectorstore():
    print("=" * 60)
    print("HR ASSISTANT - KNOWLEDGE BASE INGESTION")
    print("=" * 60)

    docs = load_documents()
    if not docs:
        print("No documents found in hr_assistant/knowledge_base/. Aborting.")
        return False

    all_chunks = []
    all_metadata = []

    print(f"\n[STEP 1] Chunking {len(docs)} document(s)...")
    for filename, (text, title) in docs.items():
        chunks = chunk_text(text)
        print(f"  - {title}: {len(chunks)} chunk(s)")
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadata.append({
                "text": chunk,
                "source": filename,
                "title": title,
            })

    print(f"\n[STEP 2] Creating embeddings with Ollama ({EMBEDDING_MODEL})...")
    try:
        embeddings = create_embeddings(all_chunks)
    except Exception as e:
        print(f"Failed to create embeddings: {e}")
        print("Make sure Ollama is running: ollama serve")
        return False

    print("\n[STEP 3] Building FAISS index...")
    embeddings_array = np.array(embeddings, dtype=np.float32)
    dimension = embeddings_array.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)
    print(f"  Index created with {index.ntotal} vectors (dim={dimension})")

    print("\n[STEP 4] Saving HR vectorstore...")
    idx_path = os.path.join(VECTOR_STORE_DIR, "hr_faiss_index.bin")
    meta_path = os.path.join(VECTOR_STORE_DIR, "hr_metadata.pkl")

    faiss.write_index(index, idx_path)
    with open(meta_path, "wb") as f:
        pickle.dump(all_metadata, f)

    print(f"  Saved: {idx_path}")
    print(f"  Saved: {meta_path}")

    print("\n" + "=" * 60)
    print("HR VECTORSTORE CREATED SUCCESSFULLY")
    print("=" * 60)
    print(f"Documents ingested : {len(docs)}")
    print(f"Total chunks        : {len(all_chunks)}")
    print(f"Embedding dimension : {dimension}")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        ollama.list()
        print("Ollama is running\n")
    except Exception as e:
        print(f"Ollama not accessible: {e}")
        print("Start Ollama first: ollama serve")
        sys.exit(1)

    success = build_hr_vectorstore()
    sys.exit(0 if success else 1)
