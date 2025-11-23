# 🛡️ Sentinel-QA: Autonomous Test Orchestrator

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![AI](https://img.shields.io/badge/AI-Ollama%20%7C%20LangChain-orange)

**Sentinel-QA** is an intelligent, privacy-first QA agent that autonomously generates comprehensive test plans and executable Selenium scripts. By ingesting project documentation and HTML structures into a RAG (Retrieval-Augmented Generation) pipeline, it ensures all test cases are strictly grounded in truth, eliminating AI hallucinations.

---

## 🚀 Key Features

* **🧠 Cognitive RAG Engine:** Ingests product specifications and UI guides into a local Vector Database (ChromaDB) for context-aware reasoning.
* **🚫 Zero Hallucinations:** Uses strict "Grounded In" citation mechanisms; if a feature isn't in the docs, the agent won't test it.
* **🕵️ Hybrid HTML Parsing:** Combines BeautifulSoup static analysis with LLM logic to map exact DOM selectors (IDs, Names, XPaths).
* **🤖 Multi-Agent Workflow:**
    * **Strategist Agent:** Creates structured JSON test plans based on business rules.
    * **Engineer Agent:** Converts test plans into runnable Python Selenium 4 scripts.
* **🔒 Privacy First:** Runs 100% locally using **Ollama** (Llama 3) and local embeddings. No data leaves your machine.

---

## 🛠️ System Architecture

1.  **Ingestion:** Docs (PDF/MD/TXT) + HTML are parsed, chunked, and embedded into **ChromaDB**.
2.  **Retrieval:** User queries trigger a semantic search to retrieve relevant documentation chunks.
3.  **Strategist:** An LLM generates a Pydantic-validated JSON Test Plan using retrieved context.
4.  **Engineer:** A second LLM maps the Test Plan + HTML Structure to generate Python Selenium code.

---

## ⚙️ Prerequisites

Before running the system, ensure you have the following installed:

1.  **Python 3.10+**
2.  **Ollama** (for local LLM inference).
    * [Download Ollama here](https://ollama.com/download)
    * After installing, pull the required models in your terminal:
    ```bash
    ollama pull llama3
    ollama pull nomic-embed-text
    ```

---

## 📦 Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/Sentinel-QA-Agent.git](https://github.com/YOUR_USERNAME/Sentinel-QA-Agent.git)
    cd Sentinel-QA-Agent
    ```

2.  **Set up Virtual Environment** (Recommended)
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🚦 Usage Guide

The system runs as two separate processes: the Backend API and the Frontend UI.

### Step 1: Start the Backend (Brain)
Open a terminal and run:
```bash
python backend/main.py
