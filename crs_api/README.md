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

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/crs-api.git
cd crs-api