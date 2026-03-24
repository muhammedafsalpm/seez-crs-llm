# 🎬 Conversational Recommender System (CRS) API

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Supported-orange.svg)](https://ollama.ai/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A production-ready, high-performance conversational recommender system built with FastAPI, supporting multiple LLM providers (OpenAI and Ollama) and three different recommendation approaches. Uses the LLM-REDIAL dataset for movie recommendations.

## ✨ Features

- **🤖 Three Recommendation Approaches**
  - **Few-Shot Learning**: Uses example conversations for in-context learning
  - **RAG (Retrieval-Augmented Generation)**: Retrieves similar conversations using FAISS vector search
  - **Agent-Based**: Simulates intelligent agent with tool-use capabilities

- **⚡ Performance Optimized**
  - Fully asynchronous endpoints for concurrent request handling
  - Streaming responses for real-time user experience
  - FAISS vector index for efficient similarity search
  - Redis caching support (optional)

- **🔌 Multi-LLM Provider Support**
  - **OpenAI GPT-3.5/4** (cloud-based, high quality)
  - **Ollama** (local, free, privacy-focused)
  - Easy switching via environment variables

- **📊 Comprehensive API**
  - Standard REST endpoints
  - Server-Sent Events (SSE) streaming
  - User history integration
  - Movie search functionality
  - System metrics monitoring

- **🛡️ Production-Ready**
  - Rate limiting
  - Error handling with graceful fallbacks
  - Health checks
  - Docker support
  - Full type hints and PEP 8 compliance

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the API](#running-the-api)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [License](#license)

---

## 🚀 Prerequisites

### System Requirements
- **Python**: 3.10 or higher
- **Memory**: Minimum 8GB RAM (16GB recommended for larger models)
- **Storage**: 10GB free space for models and dataset

### LLM Provider Options (Choose One)

#### Option A: OpenAI (Cloud, Paid)
- OpenAI API key with credits
- Internet connection required
- Faster responses, higher quality

#### Option B: Ollama (Local, Free) - **Recommended**
- Install Ollama from [ollama.ai](https://ollama.ai)
- No API key needed
- 100% free with no usage limits
- Models: Mistral (7B), Phi (2.7B), Llama2 (7B)

### Dataset
- LLM-REDIAL Movie dataset
- Download from [official source](https://github.com/your-repo/LLM-REDIAL) (reference paper: Findings of ACL 2024)

---

## 📁 Project Structure

```text
seez/
├── backend/
│   └── crs_api/            # FastAPI Backend
│       ├── app/            # Application logic
│       ├── data/           # FAISS index storage
│       ├── requirements.txt
│       └── .env            # Backend configuration
├── frontend/               # React (Vite) Frontend
│   ├── src/                # Component logic
│   ├── .env                # Frontend configuration
│   └── package.json
└── other/
    └── LLM_Redial/         # Dataset location
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Node.js & npm
- Ollama (for local LLM support)

### 2. Backend Setup
```bash
cd backend/crs_api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

---

## 🚀 Running the System

### 1. Start Ollama
Ensure Ollama is running with your preferred model:
```bash
ollama run phi
```

### 2. Start Backend
From `backend/crs_api`:
```bash
python run.py
```
The API will be available at `http://localhost:8000`.

### 3. Start Frontend
From `frontend`:
```bash
npm run dev
```
The UI will be available at `http://localhost:5173`.

---

## 🎯 Video Demonstration Guide

To demonstrate the system's full capabilities:
1. **Health Check**: View the status indicator in the header.
2. **Metrics**: See real-time dataset stats in the sidebar.
3. **Personalization**: Enter User ID `A30Q8X8B1S3GGT` in the Sidebar to load their specific movie history.
4. **Recommendation Modes**: 
   - Switch between **Few-Shot**, **RAG**, and **Agent** modes.
   - Use **RAG** for context-aware suggestions based on retrieved conversations.
5. **Streaming Output**: Witness real-time response generation in the chat window.

---

## 🛡️ License
MIT License - Copyright (c) 2026