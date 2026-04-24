# AutoPost AI

A full-stack Social Media Content Automation web app with **React + Tailwind + Framer Motion** frontend, **FastAPI** backend, **ChromaDB** vector database, and **Anthropic Claude** AI integration.

🌟 **All posts are stored as vector embeddings** for semantic search and intelligent duplicate detection.

## ✨ Features

- **AI-Powered Content Generation** - Generate 3 platform-optimized variants per platform using Claude
- **Semantic Search** - Find posts by meaning, not just keywords
- **Similar Post Detection** - Avoid repetition by analyzing past posts before generating
- **Multi-Platform** - Twitter, LinkedIn, Instagram with platform-specific optimization
- **Tone Selection** - Professional, Casual, Funny, Inspirational
- **Post Calendar** - Visual calendar view of scheduled posts
- **Posts Manager** - Full CRUD with filters and search
- **Dashboard** - Stats, recent posts, quick actions
- **Dark Theme** - Modern glassmorphism UI with glow effects
- **No Database Setup** - Everything runs locally with ChromaDB

## 🚀 Quick Start

See [START_HERE.md](START_HERE.md) for step-by-step instructions.

### TL;DR (3 commands):

```bash
# 1. Setup (one time only)
cd /Users/apple/Desktop/autopost\ ai/autopost-ai
./setup.sh

# 2. Terminal 1: Start Backend
cd backend && source venv/bin/activate && uvicorn main:app --reload

# 3. Terminal 2: Start Frontend
cd frontend && npm run dev
```

Then open **http://localhost:5173** 🎉

## 📊 Project Structure

```
autopost-ai/
├── backend/
│   ├── main.py                    # FastAPI app + CORS setup
│   ├── vector_db.py               # ChromaDB operations
│   ├── embeddings.py              # sentence-transformers
│   ├── routes/
│   │   ├── generate.py            # AI content generation
│   │   ├── posts.py               # CRUD endpoints
│   │   └── dashboard.py           # Stats endpoint
│   ├── requirements.txt
│   ├── .env                       # API keys (optional)
│   └── chroma_data/               # Persistent vector store
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx        # Navigation
│   │   │   ├── PostCard.jsx       # Post display
│   │   │   ├── PlatformBadge.jsx  # Platform styling
│   │   │   ├── StatsCard.jsx      # Dashboard cards
│   │   │   └── SearchBar.jsx      # Search UI
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx      # Home page
│   │   │   ├── CreatePost.jsx     # AI generation
│   │   │   ├── Calendar.jsx       # Schedule view
│   │   │   ├── Posts.jsx          # Manager
│   │   │   └── Settings.jsx       # Config
│   │   ├── api.js                 # API client
│   │   ├── App.jsx                # Router setup
│   │   └── main.jsx               # React entry
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── index.html
│
├── START_HERE.md                  # Quick start guide
├── README.md                      # This file
├── setup.sh                       # Auto setup script
└── .env.example                   # Template

```

## 🎯 How It Works

### Data Flow

1. **User enters topic** → Semantic search finds similar past posts
2. **Generate button** → Backend fetches similar posts + context
3. **Claude API call** → System prompt includes similar posts to avoid repetition
4. **Generate variants** → 3 unique captions per platform
5. **Save variant** → Embedded into ChromaDB + stored with metadata
6. **Search later** → Find posts by meaning, filter by platform/status

### Technologies

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React 18 + Vite | Fast, modern, reactive |
| Styling | Tailwind + Framer Motion | Beautiful, responsive, animated |
| Backend | FastAPI | Fast, async, built-in validation |
| Database | ChromaDB | Vector storage, semantic search |
| Embeddings | sentence-transformers | Lightweight, local |
| AI | Anthropic Claude | State-of-the-art text generation |

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Manual Setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

## 🏃 Running

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
# Server at http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# App at http://localhost:5173
```

## 🔑 API Keys (Optional)

To use real AI generation:

1. Get Claude API key from [console.anthropic.com](https://console.anthropic.com)
2. In app Settings, paste your key
3. Or set in `backend/.env`:
   ```
   ANTHROPIC_API_KEY=sk-...
   ```

Without keys, the app uses mock responses so you can still test everything!

## 📡 API Endpoints

### POST /api/generate
Generate content variants
```json
{
  "topic": "Machine learning trends",
  "platforms": ["twitter", "linkedin"],
  "tone": "professional"
}
```
Returns:
```json
{
  "twitter": ["variant 1", "variant 2", "variant 3"],
  "linkedin": ["variant 1", "variant 2", "variant 3"]
}
```

### GET /api/posts
List all posts with optional filters
```
?platform=twitter&status=published
```

### GET /api/posts/search
Semantic search
```
?q=machine+learning&n=5
```
Finds posts by semantic similarity, not keyword match!

### POST /api/posts
Create post
```json
{
  "content": "Post text",
  "metadata": {
    "platform": "twitter",
    "status": "draft",
    "tone": "professional",
    "topic": "AI",
    "scheduled_at": "",
    "created_at": "2024-01-01T12:00:00",
    "engagement": 0
  }
}
```

### POST /api/posts/{id}/publish
Mark post as published

### DELETE /api/posts/{id}
Delete post

### GET /api/dashboard/stats
Get aggregated stats

## 🗄️ ChromaDB Schema

### Collection: "posts"

Each post stored with:
- **id**: UUID (unique identifier)
- **document**: Post content text (gets embedded)
- **metadata**: 
  - platform: "twitter" | "linkedin" | "instagram"
  - status: "draft" | "scheduled" | "published"
  - tone: "professional" | "casual" | "funny" | "inspirational"
  - topic: Original topic
  - scheduled_at: ISO datetime (or "")
  - created_at: ISO datetime
  - engagement: Integer (mock data)

## 🎨 Design System

| Color | Purpose |
|-------|---------|
| `#0A0A0F` | Dark background |
| `#7C3AED` | Primary (purple) |
| `#06B6D4` | Secondary (cyan) |
| `rgba(255,255,255,0.05)` | Card background (glassmorphism) |

Fonts: **Syne** (headings), **DM Sans** (body) from Google Fonts

Effects: Blur backdrop, glow on hover, smooth transitions

## 🚨 Troubleshooting

**Backend won't start?**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**CORS errors?**
Check that frontend is on `http://localhost:5173` and backend on `http://localhost:8000`. Both must match `allow_origins` in `main.py`.

**"Cannot reach API"?**
1. Verify backend is running (`http://localhost:8000/health`)
2. Check no firewall is blocking ports 8000 and 5173
3. Make sure backend started before frontend

**ChromaDB storage?**
Posts stored in `backend/chroma_data/`. To reset:
```bash
rm -rf backend/chroma_data/
```

**Embeddings too slow?**
First run downloads the model (~50MB). Subsequent runs use cached model.

## 📚 Dependencies

### Backend
- fastapi: Web framework
- uvicorn: ASGI server
- chromadb: Vector database
- sentence-transformers: Embeddings
- anthropic: Claude API
- python-dotenv: Environment variables
- pydantic: Data validation

### Frontend
- react: UI library
- react-router-dom: Routing
- framer-motion: Animations
- tailwindcss: Styling
- vite: Build tool

## 🎯 What's Next?

Ideas for extending:
- **Real social media posting** - Integrate actual Twitter/LinkedIn/Instagram APIs
- **Scheduled tasks** - APScheduler for background posting
- **Analytics** - Track post performance, engagement metrics
- **Bulk operations** - Batch create/publish posts
- **Templates** - Save and reuse post templates
- **Collaborators** - Multi-user support with teams
- **Content calendar** - Drag-and-drop scheduling
- **A/B testing** - Compare variant performance

## 📄 License

This project is open source. Feel free to use and modify!

## 🤝 Contributing

Want to improve AutoPost AI? 
- Report bugs via issues
- Submit feature requests
- Create pull requests

## 📧 Support

See [START_HERE.md](START_HERE.md) for troubleshooting.

---

**Built with ❤️ for content creators**
