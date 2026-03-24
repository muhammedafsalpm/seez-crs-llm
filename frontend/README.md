# 🎬 CRS Studio - Frontend

A modern, high-performance conversational recommender system interface built with React and Vite. This frontend connects to the CRS API to provide real-time, streaming movie recommendations with a premium glassmorphic UI.

## ✨ Features

- **🤖 Interactive Chat**: Real-time streaming recommendations using SSE.
- **🔍 Movie Search**: Instant lookup in the LLM-REDIAL dataset.
- **📊 System Metrics**: Live monitoring of users, items, and conversations.
- **🛡️ Health Monitoring**: Integrated API status tracking.
- **🎨 Premium Design**: Glassmorphism, dark mode, and smooth micro-animations.

## 🚀 Getting Started

### Prerequisites
- **Node.js**: v18 or higher
- **Backend API**: Should be running at `http://localhost:8000`

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser at `http://localhost:5173`.

## ⚙️ Configuration

The frontend expects the API to be available on port 8000 by default. You can configure the API URL using environment variables:

Create a `.env` file:
```env
VITE_API_URL=http://localhost:8000
```

## 🛠️ Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Icons**: Lucide React
- **Styling**: Vanilla CSS (Custom Glassmorphism Design System)
- **API Client**: Axios & Fetch (for SSE)

---
Built with ❤️ for the Conversational Recommender System.
