# 🤖 AI RAG Chatbot with HR Assistant

An intelligent **Retrieval-Augmented Generation (RAG) Chatbot** built using **Python, Flask, Ollama, FAISS, and Large Language Models (LLMs)**.

The application retrieves relevant information from a knowledge base and uses it to generate context-aware responses. It also includes an **HR Assistant** for answering HR policy questions and generating professional messages.

---

## 🚀 Features

### 🤖 AI RAG Chatbot

- Retrieval-Augmented Generation (RAG)
- Context-aware AI responses
- Semantic search using embeddings
- FAISS vector database
- Local LLM inference using Ollama
- Flask-based web application

### 👨‍💼 HR Assistant

- HR policy-based question answering
- Leave policy assistance
- Work From Home (WFH) policy assistance
- Holiday calendar information
- Employee handbook queries
- Professional email generation
- WhatsApp message generation
- Retrieval-based responses to reduce hallucinations

---

## 🧠 RAG Workflow

```text
User Question
      │
      ▼
Convert Question into Embedding
      │
      ▼
Vector Similarity Search
      │
      ▼
Retrieve Relevant Documents
      │
      ▼
Provide Context to LLM
      │
      ▼
Generate AI Response
```

| Technology       | Purpose                  |
| ---------------- | ------------------------ |
| Python           | Backend Development      |
| Flask            | Web Framework            |
| Ollama           | Local LLM Inference      |
| Llama 3.2        | Large Language Model     |
| nomic-embed-text | Text Embeddings          |
| FAISS            | Vector Similarity Search |
| HTML             | Frontend                 |
| CSS              | Styling                  |
| JavaScript       | Frontend Interactions    |

rag-chatbot-hr-assistant/
│
├── app.py
├── rag.py
├── ingestion.py
├── scraper.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── hr_assistant/
│ ├── hr_rag.py
│ ├── hr_ingestion.py
│ ├── hr_routes.py
│ ├── notifier.py
│ │
│ └── knowledge_base/
│
├── static/
├── templates/
├── images/
│
├── vectorstore/
└── venv/
