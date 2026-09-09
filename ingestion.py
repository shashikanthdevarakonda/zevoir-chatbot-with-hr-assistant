"""
Ingestion Script - Create Vectorstore from Zevoir Website
=========================================================
This script scrapes Zevoir website pages, chunks the content,
creates embeddings, and stores them in FAISS index.

Run this once to create the vectorstore.
"""

import os
import pickle
import numpy as np
import sys

try:
    import requests
    from bs4 import BeautifulSoup
    import faiss
    import ollama
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run: pip install beautifulsoup4 requests faiss-cpu ollama numpy")
    sys.exit(1)

# -----------------------------------------------
# CONFIG
# -----------------------------------------------
ZEVOIR_URLS = [
    "https://zevoirtechnologies.com.au/",
    "https://zevoirtechnologies.com.au/services.html",
    "https://zevoirtechnologies.com.au/contactus.html",
]

VECTOR_STORE_DIR = "vectorstore"
EMBEDDING_MODEL = "nomic-embed-text"
CHUNK_SIZE = 300  # words per chunk
CHUNK_OVERLAP = 50  # word overlap between chunks

# -----------------------------------------------
# SETUP
# -----------------------------------------------
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# -----------------------------------------------
# SCRAPING
# -----------------------------------------------
def scrape_page(url: str) -> tuple:
    """
    Scrape a webpage and extract clean text
    
    Returns:
        (text, title) - tuple of extracted text and page title
    """
    try:
        print(f"📥 Fetching {url}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = str(soup.title.string).strip() if soup.title and soup.title.string else (url.split('/')[-1] or "Home")
        
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        # Extract clean text
        text = soup.get_text(separator='\n', strip=True)
        
        # Basic cleanup
        text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
        
        print(f"   ✅ Extracted {len(text.split())} words from {title}")
        return text, title
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Failed to fetch: {e}")
        return None, None
    except Exception as e:
        print(f"   ❌ Parsing error: {e}")
        return None, None

# -----------------------------------------------
# CHUNKING
# -----------------------------------------------
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    """
    Split text into overlapping chunks
    
    Args:
        text: Input text
        chunk_size: Number of words per chunk
        overlap: Number of overlapping words
        
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    
    step = chunk_size - overlap
    
    for i in range(0, len(words), step):
        chunk = ' '.join(words[i:i + chunk_size])
        
        # Only keep meaningful chunks (min 20 words)
        if len(chunk.split()) >= 20:
            chunks.append(chunk)
    
    return chunks

# -----------------------------------------------
# EMBEDDING
# -----------------------------------------------
def create_embeddings(texts: list, batch_size: int = 1) -> list:
    """
    Create embeddings for a list of texts using Ollama
    
    Args:
        texts: List of text chunks
        batch_size: Process batch size
        
    Returns:
        List of embedding vectors
    """
    embeddings = []
    
    for i, text in enumerate(texts):
        try:
            print(f"   🔄 Embedding {i+1}/{len(texts)}...", end='\r')
            
            response = ollama.embeddings(
                model=EMBEDDING_MODEL,
                prompt=text
            )
            
            embedding = response["embedding"]
            embeddings.append(embedding)
            
        except Exception as e:
            print(f"   ⚠️  Error embedding chunk {i+1}: {e}")
            # Use zero vector as placeholder
            embeddings.append([0.0] * 384)  # nomic-embed-text dimension
    
    print()  # New line
    return embeddings

# -----------------------------------------------
# FAISS INDEX CREATION
# -----------------------------------------------
def create_vectorstore():
    """Main ingestion pipeline"""
    
    print("\n" + "="*60)
    print("🚀 ZEVOIR VECTORSTORE CREATION")
    print("="*60)
    
    all_chunks = []
    all_metadata = []
    all_embeddings = []
    
    # -----------------------------------------------
    # Step 1: Scrape all pages
    # -----------------------------------------------
    print("\n[STEP 1] Scraping Zevoir website pages...")
    print("-" * 60)
    
    scraped_data = {}
    for url in ZEVOIR_URLS:
        text, title = scrape_page(url)
        if text:
            scraped_data[url] = (text, title)
    
    if not scraped_data:
        print("❌ No pages scraped successfully!")
        return False
    
    # -----------------------------------------------
    # Step 2: Chunk text
    # -----------------------------------------------
    print("\n[STEP 2] Chunking text into segments...")
    print("-" * 60)
    
    total_chunks = 0
    for url, (text, title) in scraped_data.items():
        chunks = chunk_text(text)
        print(f"📊 {title}: {len(chunks)} chunks")
        
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadata.append({
                "text": chunk,
                "url": url,
                "title": title,
                "length": len(chunk.split())
            })
        
        total_chunks += len(chunks)
    
    print(f"\n✅ Total chunks: {total_chunks}")
    
    # -----------------------------------------------
    # Step 3: Create embeddings
    # -----------------------------------------------
    print("\n[STEP 3] Creating embeddings with Ollama...")
    print(f"Model: {EMBEDDING_MODEL}")
    print("-" * 60)
    
    try:
        all_embeddings = create_embeddings(all_chunks)
    except Exception as e:
        print(f"❌ Failed to create embeddings: {e}")
        print("Make sure Ollama is running: ollama serve")
        return False
    
    print(f"✅ Created {len(all_embeddings)} embeddings")
    
    # -----------------------------------------------
    # Step 4: Create FAISS index
    # -----------------------------------------------
    print("\n[STEP 4] Building FAISS index...")
    print("-" * 60)
    
    try:
        embeddings_array = np.array(all_embeddings, dtype=np.float32)
        print(f"Embedding shape: {embeddings_array.shape}")
        
        # Create L2 distance index
        dimension = embeddings_array.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_array)
        
        print(f"✅ Index created with {index.ntotal} vectors")
        
    except Exception as e:
        print(f"❌ Failed to create FAISS index: {e}")
        return False
    
    # -----------------------------------------------
    # Step 5: Save vectorstore
    # -----------------------------------------------
    print("\n[STEP 5] Saving vectorstore...")
    print("-" * 60)
    
    try:
        idx_path = os.path.join(VECTOR_STORE_DIR, "faiss_index.bin")
        meta_path = os.path.join(VECTOR_STORE_DIR, "metadata.pkl")
        
        faiss.write_index(index, idx_path)
        with open(meta_path, "wb") as f:
            pickle.dump(all_metadata, f)
        
        print(f"✅ Index saved: {idx_path}")
        print(f"✅ Metadata saved: {meta_path}")
        
    except Exception as e:
        print(f"❌ Failed to save vectorstore: {e}")
        return False
    
    # -----------------------------------------------
    # Summary
    # -----------------------------------------------
    print("\n" + "="*60)
    print("✅ VECTORSTORE CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"Total pages: {len(scraped_data)}")
    print(f"Total chunks: {total_chunks}")
    print(f"Embedding dimension: {dimension}")
    print(f"Storage directory: {VECTOR_STORE_DIR}/")
    print("="*60)
    
    return True

# -----------------------------------------------
# MAIN
# -----------------------------------------------
if __name__ == "__main__":
    print("\n" + "="*60)
    print("ZEVOIR CHATBOT - VECTORSTORE INGESTION")
    print("="*60)
    print("\nPrerequisites:")
    print("✓ Ollama installed and running")
    print("✓ Models: ollama pull nomic-embed-text")
    print("="*60)
    
    # Check Ollama
    try:
        ollama.list()
        print("\n✅ Ollama is running\n")
    except Exception as e:
        print(f"\n❌ Ollama not accessible: {e}")
        print("Start Ollama first: ollama serve\n")
        sys.exit(1)
    
    # Run ingestion
    success = create_vectorstore()
    
    if success:
        print("\n🎉 You can now run: python app.py")
        sys.exit(0)
    else:
        print("\n⚠️  Ingestion failed. Check errors above.")
        sys.exit(1)
