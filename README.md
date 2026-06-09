<h1 align="center"> 🤖 AI Tech News Agent</h1>

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

> An intelligent AI agent that **continuously monitors technology news** and sends **Telegram notifications** whenever a highly important technology event occurs.

---

## 📋 Overview

AI Tech News Agent is a production-ready, fully automated system that:

- 📡 **Monitors** five major tech news RSS feeds every 30 minutes
- 🧠 **Analyses** each article using the OpenAI API (summary, bullet points, impact scoring)
- 📊 **Scores** articles on Impact (1–10) and Relevance (1–10)
- 🔔 **Notifies** you on Telegram when a high-impact event happens (score > 8)
- 💾 **Stores** everything in a lightweight SQLite database
- 🌐 **Exposes** a REST API (FastAPI) for querying processed articles

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔄 Auto-fetching | Polls 5 RSS feeds every 30 minutes |
| 🤖 AI analysis | GPT-powered summary, bullet points & "Why It Matters" |
| 📈 Impact scoring | 1–10 scale with category-aware bias |
| 📲 Telegram alerts | Instant notifications for high-impact news |
| 🗄️ SQLite storage | Persistent, zero-config database |
| 🚀 FastAPI server | Health check, latest articles, full news list |
| ⚙️ APScheduler | Reliable background job scheduling |
| 🛡️ Error handling | Graceful degradation for every external service |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                    RSS Sources                        │
│  Google News · TechCrunch · Reuters · Verge · Ars    │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │  News Fetcher  │   feedparser
              └───────┬────────┘
                      │
                      ▼
              ┌────────────────┐
              │ OpenAI Analysis│   gpt-4o-mini
              └───────┬────────┘
                      │
                      ▼
              ┌────────────────┐
              │ Impact Scoring │   1 – 10
              └───────┬────────┘
                      │
                      ▼
              ┌────────────────┐
              │ SQLite Database│   news.db
              └───────┬────────┘
                      │
            ┌─────────┴──────────┐
            ▼                    ▼
  ┌──────────────────┐  ┌───────────────┐
  │ Telegram Notify  │  │  FastAPI API  │
  │  (score > 8)     │  │  /health etc. │
  └──────────────────┘  └───────────────┘
```

---

## 📁 Project Structure

```
ai-tech-news-agent/
├── app/
│   ├── __init__.py          # Package marker
│   ├── main.py              # FastAPI app + lifespan + endpoints
│   ├── scheduler.py         # Pipeline orchestrator (fetch → analyse → notify)
│   ├── news_fetcher.py      # RSS feed fetcher (feedparser)
│   ├── ai_ranker.py         # OpenAI analysis & scoring
│   ├── notifier.py          # Telegram notification sender
│   ├── database.py          # SQLite persistence layer
│   ├── models.py            # Pydantic models
│   ├── config.py            # Settings from environment variables
│   └── data/
│       └── news.db          # Auto-created SQLite database
├── requirements.txt
├── .env.example
├── .gitignore
├── Procfile                 # Railway / Render deployment
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.11+**
- An **OpenAI API key** ([platform.openai.com](https://platform.openai.com/api-keys))
- A **Telegram Bot Token** + **Chat ID** (see setup below)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/ai-tech-news-agent.git
cd ai-tech-news-agent

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and add your keys (see section below)
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | Your OpenAI API key |
| `OPENAI_MODEL` | ❌ | Model to use (default: `gpt-4o-mini`) |
| `TELEGRAM_BOT_TOKEN` | ✅ | Telegram bot token from BotFather |
| `TELEGRAM_CHAT_ID` | ✅ | Target chat / group / channel ID |
| `DB_PATH` | ❌ | Custom SQLite path (default: `app/data/news.db`) |
| `FETCH_INTERVAL_MINUTES` | ❌ | Poll interval (default: `30`) |
| `IMPACT_THRESHOLD` | ❌ | Minimum score to trigger alerts (default: `8`) |

---

## 🤖 Telegram Bot Setup

### 1. Create a Bot

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts.
3. Copy the **bot token** — set it as `TELEGRAM_BOT_TOKEN`.

### 2. Get Your Chat ID

1. Start a chat with your new bot (send `/start`).
2. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find `"chat":{"id": <number>}` in the JSON response.
4. Set that number as `TELEGRAM_CHAT_ID`.

> **Tip:** For a group chat, add the bot to the group first, then call `getUpdates`.

---

## 💻 Local Development

```bash
# Load environment variables (if using dotenv)
# The app reads .env automatically via python-dotenv

# Start the development server
uvicorn app.main:app --reload --port 8000
```

The server will start at **http://localhost:8000**. The scheduler runs in the background and triggers immediately on startup.

---

## ▶️ Running the Application

```bash
# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### What happens on startup

1. SQLite database is initialised (auto-creates `app/data/news.db`).
2. APScheduler starts a background job every 30 minutes.
3. The pipeline runs once immediately.
4. FastAPI serves the REST API.

---

## 🚄 Railway Deployment

1. Push the repo to GitHub.
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**.
3. Select the repository.
4. Add environment variables in the Railway dashboard:
   - `OPENAI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
5. Railway auto-detects the `Procfile`. Click **Deploy**.

---

## 🎨 Render Deployment

1. Push the repo to GitHub.
2. Go to [render.com](https://render.com) → **New Web Service**.
3. Connect your repository.
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add the three environment variables.
6. Click **Create Web Service**.

---

## 📡 API Documentation

Once the server is running, interactive docs are available at:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | API status |
| `GET` | `/health` | Health check (DB + scheduler) |
| `GET` | `/latest` | 10 most recent articles |
| `GET` | `/news` | 50 most recent articles |

### Example Response — `GET /latest`

```json
[
  {
    "id": 42,
    "title": "OpenAI Releases GPT-5",
    "url": "https://example.com/article",
    "source": "TechCrunch",
    "summary": "OpenAI has released GPT-5 with significant improvements...",
    "impact_score": 10,
    "relevance_score": 10,
    "published_date": "2025-01-15T10:30:00Z",
    "notification_sent": true,
    "created_at": "2025-01-15T10:35:00Z"
  }
]
```

---

## 📲 Example Notification

```
🚀 Breaking Tech Update

Headline:
OpenAI Releases GPT-5 with Multimodal Reasoning

Summary:
• GPT-5 introduces advanced multimodal reasoning capabilities
• Performance benchmarks show 2× improvement over GPT-4
• Available immediately via API with new pricing tiers

Why It Matters:
This release sets a new industry standard for large language models
and could accelerate AI adoption across enterprise applications.

Impact Score: 10/10

Source:
https://techcrunch.com/2025/01/15/openai-gpt5
```

---

## 📸 Screenshots

> After running the application, the interactive API docs are available at `/docs`:
>
> - Swagger UI at `http://localhost:8000/docs`
> - Health endpoint at `http://localhost:8000/health`
> - Latest articles at `http://localhost:8000/latest`

---

## 🔮 Future Improvements

- [ ] Add more RSS feeds (Hacker News, Wired, MIT Tech Review)
- [ ] Support multiple Telegram channels (per-topic routing)
- [ ] Add a web dashboard for browsing articles
- [ ] Implement keyword-based custom alerts
- [ ] Add email notifications as an alternative channel
- [ ] Cache OpenAI responses to reduce API costs
- [ ] Add unit and integration tests
- [ ] Migrate to PostgreSQL for production scale
- [ ] Containerise with Docker for easier deployment
- [ ] Add Prometheus metrics endpoint

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m "Add amazing feature"`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a **Pull Request**

Please ensure your code follows the existing style and includes type hints.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ using Python, FastAPI, and OpenAI
</p>
"# AI-News_Agent" 
