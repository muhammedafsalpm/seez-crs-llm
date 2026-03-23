# Conversational Recommender System (CRS) API

A production-ready FastAPI-based system for movie recommendations using the LLM-REDIAL dataset.

## Prerequisites
- Python 3.10+
- OpenAI API Key
- LLM-REDIAL Movie dataset (located at `../LLM_Redial/Movie`)

## Setup

1. **Environment Variables**:
   Copy `.env.example` to `.env` and add your `OPENAI_API_KEY`.
   ```bash
   cp .env.example .env
   ```

2. **Data Path**:
   Ensure the `DATA_PATH` in `.env` points to your dataset. (Default is `../LLM_Redial/Movie`).

---

## Running Without Docker

### 1. Install Dependencies
It's recommended to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the API
```bash
python run.py
```
The API will be available at `http://localhost:8000`. You can access the Interactive Swagger documentation at `http://localhost:8000/docs`.

---

## Running With Docker

### 1. Build and Start
Ensure Docker and Docker Compose are installed:
```bash
docker-compose up --build
```

### 2. Use the API
The containerized API will be available at `http://localhost:8000`.

---

## API Endpoints

- `GET /`: Health check.
- `POST /api/v1/recommend`: Get movie recommendations (JSON).
- `POST /api/v1/recommend/stream`: Stream recommendations as they are generated.
- `GET /api/v1/user/{user_id}`: Get user interaction history.
- `GET /api/v1/movies/search?q=query`: Search items.
- `GET /api/v1/metrics`: System usage metrics.
