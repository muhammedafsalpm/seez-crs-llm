# 🚀 CRS Backend - FastAPI API

This is the backend for the Conversational Recommender System (CRS), a high-performance recommendation engine built with FastAPI and Ollama.

## 📁 Project Structure

```text
backend/crs_api/
├── app/
│   ├── api/            # API Route handlers
│   ├── core/           # Core logic (Lifespan, prompts)
│   ├── models/         # Pydantic schemas
│   ├── services/       # Recommendation services (RAG, Few-Shot, Agent)
│   ├── utils/          # Utilities (Data loader, LLM client)
│   └── vector_store/   # FAISS Index implementation
├── data/               # Vector index storage
├── .env                # Configuration
└── requirements.txt    # Dependencies
```

## 🛠️ Setup & Running

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**:
   Ensure `.env` contains the correct `DATA_PATH` pointing to `other/LLM_Redial/Movie`.

3. **Launch Server**:
   ```bash
   python run.py
   ```

The API documentation will be available at `http://localhost:8000/docs`.

---
**For full system setup including the UI, please refer to the [Root README.md](../../README.md).**