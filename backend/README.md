# Regulatory Compliance Assistant (Backend)

## Architecture
This system uses a **RAG (Retrieval-Augmented Generation)** architecture specifically ensuring:
1.  **Accuracy**: Using FAISS for dense vector retrieval.
2.  **Context**: MongoDB stores conversation history for multi-turn understanding.
3.  **Reasoning**: `pydantic-ai` with Google Gemini 1.5 Flash (as proxy for 2.5-lite request) for structured compliance audits.

## Tech Stack
-   **Framework**: FastAPI
-   **LLM**: Google Gemini
-   **Vector DB**: FAISS (CPU)
-   **Database**: MongoDB Atlas (Cloud - Chat History)
-   **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)

## Setup

1.  **Environment Variables**: 
    Create a `.env` file in the `backend` directory with:
    ```env
    GROQ_API_KEY=your_groq_api_key
    MONGODB_URI=your_mongodb_atlas_connection_string
    ```
    (See `.env.example` for template)
2.  **Install Dependencies**:
    ```bash
    cd backend
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```
3.  **Run**:
    ```bash
    uvicorn main:app --reload
    ```

## Endpoints
-   `POST /api/v1/ingest/`: Upload PDF regulatory docs.
-   `POST /api/v1/query/`: Ask compliance questions. (Auto-saves history).
