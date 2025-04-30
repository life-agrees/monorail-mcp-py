# Monorail MCP Server & Dashboard

A self-hosted Model Context Protocol (MCP) server for Monorail’s on-chain quote & trade APIs, plus a Streamlit dashboard to visualize and track failed trades in real time.

---

## 🚀 Features

- **/quote**: Fetch swap quotes across 11 exchanges (7k+ tokens).
- **/trade/{token_pair}**: Request ready-to-send transaction data.
- **Automatic retries & failure capture**:  
  - Failed calls get logged to SQLite.  
  - Slack alerts on each failure.  
  - Webhook callbacks support custom listeners.
- **/failed-trades**: Browse persisted failures via API.
- **Streamlit Dashboard**:  
  - Bar chart of failures by token pair  
  - Detailed trade-by-trade view  

---

## 🛠️ Tech Stack

- **FastAPI** — MCP server  
- **Pydantic** — request validation  
- **HTTPX** — async HTTP client with retry logic  
- **SQLModel (SQLite)** — lightweight persistence  
- **Slack SDK** — real-time alerts  
- **Streamlit** — dashboard UI  
- **Docker & Docker Compose** — containerized deployment  
- **Railway.app** — hosting  

---

## 📦 Getting Started

1. **Clone & configure**  
   ```bash
   git clone https://github.com/life-agrees/monorail-mcp-py
   cd monorail-mcp-py
   cp .env.example .env
   # Edit .env with your BASE_URL, SLACK_BOT_TOKEN, SLACK_CHANNEL…
   
2. **Build & run API**
   ```bash
   docker build -t monorail-app .
   docker run -d -p 8000:8000 --env-file .env monorail-app
3. **Build & run Dashboard**
    ```bash
    docker build -f Dockerfile.dashboard -t monorail-dashboard .
    docker run -d -p 8501:8501 monorail-dashboard
4. **Visit**
   API docs: http://localhost:8000/docs
   Dashboard: http://localhost:8501

## ☁️ Deploy
1. **Pushed to Docker Hub**
   ```bash
   docker tag monorail-app lifeagrees/monorail-app:latest
   docker push lifeagrees/monorail-app:latest
2. **Deployed on Railway**
   API:https://monorail-mcp-py-production.up.railway.app/docs
   DASHBOARD:https://monorail-mcp-py-production-ffd0.up.railway.app

## What This Solves
1. Speeds up AI agents’ access to aggregated on-chain swap quotes & trades
2. Reliability: automatic retry/catch + failure logging & alerting
3. Visibility: real-time dashboard & API for audit & debugging
