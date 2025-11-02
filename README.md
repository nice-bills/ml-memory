```markdown
# Memory Bank - AI Chatbot with Persistent Memory

<div align="center">

![Memory Bank Banner](./docs/images/banner.png)
*Add a banner image here - suggestion: A sleek dark-themed header with the app name and a brain/memory icon*

An intelligent ML Engineering chatbot powered by Groq's LLM and Pinecone's vector database, featuring real-time streaming responses and persistent conversational memory.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-16.0-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.120-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Docker Deployment](#-docker-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

Memory Bank is a production-ready AI chatbot designed specifically for Machine Learning Engineering queries. Unlike traditional chatbots, it maintains **persistent memory** across conversations using vector embeddings, allowing it to recall previous interactions and provide contextually aware responses.

The system combines:
- **Groq's LLM** (Llama 3.1 8B) for fast, intelligent responses
- **Pinecone Vector Database** for semantic memory storage and retrieval
- **Streaming API** for real-time response delivery
- **Modern React UI** with syntax highlighting and markdown rendering

![Chat Interface](./docs/images/chat-interface.png)
*Add a screenshot here showing the chat interface in action*

---

## ✨ Key Features

### 🧠 Intelligent Memory System
- **Vector-based memory storage** using sentence transformers
- **Semantic search** to retrieve relevant context from past conversations
- **Automatic memory management** with configurable thresholds
- **Role-aware storage** (user vs assistant messages)

### ⚡ Real-time Streaming
- **Live response streaming** from Groq API
- **Progressive rendering** in the UI
- **Low-latency delivery** for improved UX

### 💻 Developer-Friendly
- **Code syntax highlighting** for 50+ languages
- **Copy-to-clipboard** functionality for code blocks
- **Markdown rendering** with custom styling
- **Dark mode** optimized interface

### 🎭 Specialized Persona
- **Principal ML Engineer** persona with 15+ years experience
- **MLOps expertise** across the entire ML lifecycle
- **Practical, production-focused** guidance
- **Patient mentor** approach to complex topics

### 🏗️ Production Ready
- **Docker containerization** for easy deployment
- **CORS configuration** for secure API access
- **Error handling** and graceful degradation
- **Environment-based configuration**

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Next.js 16 + React 19 + TypeScript                  │   │
│  │  - ChatStreaming Component                           │   │
│  │  - Real-time message streaming                       │   │
│  │  - Syntax highlighting (Prism)                       │   │
│  │  - Markdown rendering                                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP Streaming
                      │ (port 9696)
┌─────────────────────▼───────────────────────────────────────┐
│                         Backend                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  FastAPI + Python 3.12                               │   │
│  │  ┌─────────────────┐    ┌─────────────────────┐    │   │
│  │  │  Chat Endpoint  │───▶│  Groq LLM Client    │    │   │
│  │  │  /chat (POST)   │    │  (Llama 3.1 8B)     │    │   │
│  │  └────────┬────────┘    └─────────────────────┘    │   │
│  │           │                                          │   │
│  │           ▼                                          │   │
│  │  ┌─────────────────┐    ┌─────────────────────┐    │   │
│  │  │ Memory Manager  │───▶│  Pinecone Vector    │    │   │
│  │  │ (brain.py)      │    │  Database           │    │   │
│  │  └─────────────────┘    └─────────────────────┘    │   │
│  │           │                        │                │   │
│  │           ▼                        ▼                │   │
│  │  ┌─────────────────┐    ┌─────────────────────┐    │   │
│  │  │ Sentence        │    │ Semantic Search     │    │   │
│  │  │ Transformers    │    │ (Cosine Similarity) │    │   │
│  │  │ (MiniLM-L6-v2)  │    │ Threshold: 0.7      │    │   │
│  │  └─────────────────┘    └─────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

![Architecture Diagram](./docs/images/architecture.png)
*Add a visual architecture diagram here*

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12 | Runtime environment |
| **FastAPI** | 0.120+ | Web framework & API |
| **Groq** | 0.33+ | LLM API client |
| **Pinecone** | Latest | Vector database |
| **Sentence Transformers** | 5.1.2 | Embedding generation |
| **Transformers** | 4.57.1 | Hugging Face models |
| **Uvicorn** | 0.38+ | ASGI server |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 16.0.1 | React framework |
| **React** | 19.2.0 | UI library |
| **TypeScript** | 5.x | Type safety |
| **Tailwind CSS** | 4.x | Styling |
| **React Markdown** | 10.1+ | Markdown rendering |
| **React Syntax Highlighter** | 16.1+ | Code highlighting |
| **shadcn/ui** | Latest | UI components |

### DevOps
- **Docker** & **Docker Compose** - Containerization
- **UV** - Fast Python package installer
- **Node 20 Alpine** - Lightweight Node.js image

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+** ([Download](https://www.python.org/downloads/))
- **Node.js 20+** ([Download](https://nodejs.org/))
- **Docker & Docker Compose** ([Download](https://www.docker.com/))
- **Git** ([Download](https://git-scm.com/))

You'll also need accounts and API keys for:
- **Groq** ([Sign up](https://console.groq.com/))
- **Pinecone** ([Sign up](https://www.pinecone.io/))

---

## 🚀 Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/memory-bank.git
   cd memory-bank
   ```

2. **Set up environment variables**
   ```bash
   # Create backend .env file
   cd backend
   cp .env.example .env
   # Edit .env with your API keys (see Configuration section)
   ```

3. **Build and run with Docker Compose**
   ```bash
   cd ..
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:9696
   - API Docs: http://localhost:9696/docs

### Option 2: Local Development

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the backend server**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 9696
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   # Create .env.local file
   echo "NEXT_PUBLIC_API_URL=http://localhost:9696" > .env.local
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to http://localhost:3000

---

## ⚙️ Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Required API Keys
PINECONE_API_KEY=your_pinecone_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Optional Configuration
# PINECONE_ENVIRONMENT=us-east-1-aws  # Default region
# MODEL_NAME=llama-3.1-8b-instant     # Groq model
# EMBEDDING_MODEL=all-MiniLM-L6-v2    # Sentence transformer model
```

**Getting API Keys:**

1. **Pinecone API Key**
   - Sign up at [pinecone.io](https://www.pinecone.io/)
   - Navigate to API Keys section
   - Create a new API key
   - Copy the key value

2. **Groq API Key**
   - Sign up at [console.groq.com](https://console.groq.com/)
   - Go to API Keys section
   - Generate a new key
   - Copy the key value

### Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:9696

# For production deployment
# NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

### Docker Compose Configuration

The `docker-compose.yml` automatically handles environment variables:

```yaml
services:
  backend:
    env_file:
      - ./backend/.env  # Loads backend environment variables
    ports:
      - "9696:9696"
  
  frontend:
    environment:
      NEXT_PUBLIC_API_URL: http://backend:9696  # Uses Docker service name
    ports:
      - "3000:3000"
```

---

## 🎮 Usage

### Basic Conversation Flow

1. **Start a conversation**
   ```
   User: "What is gradient descent?"
   ```

2. **Receive streaming response**
   - The AI responds in real-time
   - Response is streamed word-by-word
   - Previous context is automatically recalled

3. **Copy code blocks**
   - Hover over any code block
   - Click the "Copy code" button
   - Paste into your editor

![Code Highlighting](./docs/images/code-highlight.png)
*Add a screenshot showing code block with copy button*

### Advanced Features

#### Memory Search
The system automatically:
- Stores all messages with vector embeddings
- Searches for relevant context (top 3 matches)
- Filters by similarity score (threshold: 0.7)
- Injects context into the prompt

#### Keyboard Shortcuts
- `Enter` - Send message
- `Shift + Enter` - New line in textarea
- Textarea auto-resizes (1-6 rows)

#### Markdown Support
The chatbot supports:
- **Bold** and *italic* text
- `Inline code`
- Code blocks with syntax highlighting
- Lists and links
- Headers and blockquotes

---

## 📁 Project Structure

```
memory-bank/
│
├── backend/                    # Python FastAPI backend
│   ├── .venv/                 # Virtual environment (gitignored)
│   ├── __pycache__/           # Python cache (gitignored)
│   ├── data/                  # Data directory (gitignored)
│   │
│   ├── app.py                 # Main FastAPI application
│   ├── brain.py               # Memory management system
│   ├── requirements.txt       # Python dependencies
│   ├── pyproject.toml         # Python project config
│   ├── dockerfile             # Backend Docker image
│   ├── .env                   # Environment variables (gitignored)
│   ├── .gitignore            # Backend gitignore
│   └── .python-version        # Python version specification
│
├── frontend/                   # Next.js React frontend
│   ├── node_modules/          # NPM packages (gitignored)
│   ├── .next/                 # Next.js build (gitignored)
│   │
│   ├── public/                # Static assets
│   │   ├── file.svg
│   │   ├── globe.svg
│   │   ├── next.svg
│   │   ├── vercel.svg
│   │   └── window.svg
│   │
│   ├── src/
│   │   ├── app/               # Next.js app directory
│   │   │   ├── globals.css   # Global styles
│   │   │   ├── layout.tsx    # Root layout
│   │   │   └── page.tsx      # Home page
│   │   │
│   │   ├── components/        # React components
│   │   │   ├── ui/           # shadcn/ui components
│   │   │   │   ├── avatar.tsx
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── conversation-bar.tsx
│   │   │   │   ├── conversation.tsx
│   │   │   │   ├── live-waveform.tsx
│   │   │   │   ├── message.tsx
│   │   │   │   ├── response.tsx
│   │   │   │   ├── separator.tsx
│   │   │   │   └── textarea.tsx
│   │   │   └── ChatStreaming.tsx  # Main chat component
│   │   │
│   │   └── lib/
│   │       └── utils.ts      # Utility functions
│   │
│   ├── components.json        # shadcn/ui config
│   ├── dockerfile             # Frontend Docker image
│   ├── eslint.config.mjs      # ESLint configuration
│   ├── next.config.ts         # Next.js configuration
│   ├── package.json           # NPM dependencies
│   ├── postcss.config.mjs     # PostCSS configuration
│   ├── tsconfig.json          # TypeScript configuration
│   ├── .gitignore            # Frontend gitignore
│   └── README.md             # Frontend README
│
├── docker-compose.yml         # Docker orchestration
├── .gitignore                # Root gitignore
└── README.md                 # This file
```

---

## 📚 API Documentation

### POST `/chat`

Stream AI responses with persistent memory.

**Request Body:**
```json
{
  "user_input": "Explain backpropagation in neural networks"
}
```

**Response:**
- **Type:** `text/plain` (streaming)
- **Content:** Streamed text chunks

**Example cURL:**
```bash
curl -X POST http://localhost:9696/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input": "What is gradient descent?"}'
```

**Response Flow:**
1. User message stored in Pinecone
2. Semantic search for relevant context
3. Prompt constructed with context
4. Groq API streams response
5. Response saved to memory
6. Chunks yielded to client

### GET `/docs`

Interactive API documentation powered by Swagger UI.

**Access:** http://localhost:9696/docs

![API Docs](./docs/images/api-docs.png)
*Add a screenshot of the Swagger UI here*

---

## 🔧 Development

### Backend Development

#### Running Tests
```bash
cd backend
pytest tests/
```

#### Testing Memory System Standalone
```bash
cd backend
python brain.py
```

This starts an interactive session where you can:
- Add memories
- Search memories
- Test vector similarity

#### Linting & Formatting
```bash
# Install dev dependencies
pip install black flake8 mypy

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Frontend Development

#### Component Development
```bash
cd frontend
npm run dev
```

Hot reload is enabled - changes appear instantly.

#### Adding New UI Components
```bash
# Using shadcn/ui CLI
npx shadcn@latest add [component-name]
```

#### Linting & Formatting
```bash
# Lint code
npm run lint

# Type checking
npx tsc --noEmit
```

#### Building for Production
```bash
npm run build
npm start
```

---

## 🐳 Docker Deployment

### Production Deployment

1. **Update environment variables**
   ```bash
   # backend/.env
   PINECONE_API_KEY=prod_key_here
   GROQ_API_KEY=prod_key_here
   ```

2. **Update frontend API URL**
   ```yaml
   # docker-compose.yml
   frontend:
     environment:
       NEXT_PUBLIC_API_URL: https://your-api-domain.com
   ```

3. **Build and deploy**
   ```bash
   docker-compose -f docker-compose.yml up --build -d
   ```

### Multi-stage Builds

Both Dockerfiles use multi-stage builds for optimization:

**Backend:**
- Uses `uv` for fast dependency installation
- Creates virtual environment in container
- Minimal Python 3.13 slim image

**Frontend:**
- Builder stage compiles Next.js
- Runner stage serves static files
- Node 20 Alpine for minimal size

### Docker Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Remove volumes
docker-compose down -v

# Rebuild specific service
docker-compose up --build backend
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Missing Pinecone API key" Error

**Symptom:** Backend fails to start
```
ValueError: Missing Pinecone API key
```

**Solution:**
- Verify `.env` file exists in `backend/`
- Check `PINECONE_API_KEY` is set correctly
- Ensure no extra spaces around the key

#### 2. "Failed to initialize Pinecone memory" Error

**Symptom:** Connection to Pinecone fails
```
Failed to initialize Pinecone memory: <error>
```

**Solution:**
- Check API key is valid
- Verify Pinecone account is active
- Check network connectivity
- Review Pinecone region settings

#### 3. CORS Errors in Browser

**Symptom:** Frontend can't connect to backend
```
Access to fetch at 'http://localhost:9696' has been blocked by CORS policy
```

**Solution:**
- Verify backend is running on port 9696
- Check `NEXT_PUBLIC_API_URL` matches backend URL
- In Docker, use service name: `http://backend:9696`

#### 4. Streaming Not Working

**Symptom:** Messages appear all at once, not streamed

**Solution:**
- Check network isn't buffering responses
- Verify `stream=True` in Groq API call
- Test with cURL to isolate issue

#### 5. Docker Build Fails

**Symptom:** `docker-compose up` fails

**Solution:**
```bash
# Clean Docker cache
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose up --build --force-recreate
```

### Debug Mode

Enable verbose logging:

**Backend:**
```python
# app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**
```typescript
// ChatStreaming.tsx
console.log('Message:', msg);
console.log('Chunk received:', chunk);
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests if applicable
   - Update documentation

4. **Commit with conventional commits**
   ```bash
   git commit -m "feat: add amazing feature"
   git commit -m "fix: resolve streaming issue"
   git commit -m "docs: update README"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Document functions with docstrings

**TypeScript:**
- Use ESLint configuration
- Follow React best practices
- Use functional components

### Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) - Lightning-fast LLM inference
- [Pinecone](https://www.pinecone.io/) - Vector database platform
- [Hugging Face](https://huggingface.co/) - Sentence transformers
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful UI components
- [Vercel](https://vercel.com/) - Next.js framework

---

## 📞 Support

Having issues? Here's how to get help:

1. **Check the [Troubleshooting](#-troubleshooting) section**
2. **Search [existing issues](https://github.com/yourusername/memory-bank/issues)**
3. **Open a new issue** with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python/Node version)

---

## 🗺️ Roadmap

- [ ] **v1.1** - User authentication & multi-user support
- [ ] **v1.2** - Conversation history management
- [ ] **v1.3** - Voice input/output
- [ ] **v1.4** - File upload & analysis
- [ ] **v2.0** - Multi-modal support (images, PDFs)
- [ ] **v2.1** - Fine-tuned custom models
- [ ] **v2.2** - RAG with external knowledge bases

---

<div align="center">

Made with ❤️ by [Your Name]

[⬆ Back to Top](#memory-bank---ai-chatbot-with-persistent-memory)

</div>
```

## 📸 Image Requirements

Create these images and place them in the `docs/images/` directory:

### 1. `banner.png` (1200x400px)
- Dark gradient background (purple #6366f1 to blue #3b82f6)
- Large white text: "Memory Bank"
- Subtitle: "AI Chatbot with Persistent Memory"
- Brain/memory icon on the left
- Modern, clean design

### 2. `chat-interface.png` (1200x800px)
Screenshot requirements:
- Show 3-4 messages in conversation
- Include both user (blue) and AI (dark gray) messages
- Show at least one code block with syntax highlighting
- Display the input area at bottom
- Dark mode interface

### 3. `code-highlight.png` (800x600px)
Close-up screenshot showing:
- A Python code block with syntax highlighting
- The "Copy code" button visible (hover state)
- Language label "python" in top-left
- Dark code editor theme

### 4. `architecture.png` (1000x800px)
Diagram showing:
- React/Next.js icon → FastAPI icon → Pinecone icon
- Groq logo
- Arrows showing data flow
- Labels for each component
- Use tools like draw.io, Excalidraw, or Figma

### 5. `api-docs.png` (1200x800px)
Screenshot of:
- Swagger UI at http://localhost:9696/docs
- Show the `/chat` endpoint expanded
- Display request body schema
- Show example response

You can create these using:
- **Figma** or **Canva** for banner
- **Screenshots** from your running app
- **draw.io** or **Excalidraw** for architecture diagram
- **Browser screenshots** for API docs