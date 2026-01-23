# 🚀 Career Recommender - AI-Powered Career Discovery Platform

<div align="center">

![Career Recommender](https://img.shields.io/badge/Career-Recommender-1B4D3E?style=for-the-badge&logo=rocket&logoColor=C5E500)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-LLM-black?style=for-the-badge)

**Complete career discovery platform with AI-powered recommendations, dynamic career matching, personalized roadmaps, and real-time market insights.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Tech Stack](#-tech-stack)

</div>

---

## ✨ Features

### 🎯 **Intelligent Career Matching**
- **LLM-Powered Matching**: Uses Ollama LLM (qwen2.5:7b-instruct) to dynamically match careers based on your actual interests, skills, and hobbies
- **Context-Aware**: Understands nuanced inputs like "organic farming" → Agriculture careers, "game development" → Gaming industry careers
- **No Static Categories**: Dynamic career discovery from LLM's knowledge base, not limited to predefined lists

### 📊 **Comprehensive Analysis**
- **50+ Career Paths**: Covering Technology, Finance, Healthcare, Education, Business, Design, Agriculture, Arts, and more
- **Market Insights**: Real-time news integration for career-specific market trends
- **Salary Information**: Detailed salary ranges in Indian Rupees (LPA)
- **Growth Projections**: Industry growth rates and demand analysis

### 🗺️ **Personalized Roadmaps**
- **Phase-Based Learning**: 4-phase career development roadmaps (Foundation → Skills → Specialization → Launch)
- **150+ Word Descriptions**: Detailed, actionable guidance for each phase
- **Education-Specific**: Roadmaps tailored to your education level
- **Milestone Tracking**: Clear milestones and deliverables for each phase

### 🎨 **Modern UI/UX**
- **Prometheus Theme**: Elegant dark green (#1B4D3E) and lime (#C5E500) color scheme
- **Interactive Elements**: Partify-style puzzle interactions on landing page
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Smooth Animations**: Framer Motion powered transitions and effects

### 🔒 **Privacy First**
- **Completely Offline**: All processing happens locally
- **No Data Collection**: Your career interests stay on your machine
- **Local LLM**: Uses Ollama running on your own hardware

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 18 + TypeScript | Modern, type-safe UI |
| **Styling** | Tailwind CSS | Utility-first styling |
| **Animations** | Framer Motion | Smooth interactions |
| **Build Tool** | Vite | Fast development & builds |
| **Backend** | Python FastAPI | High-performance API |
| **LLM** | Ollama (qwen2.5:7b-instruct) | Local AI inference |
| **RAG** | FAISS + Sentence-Transformers | Knowledge retrieval |
| **Embeddings** | all-MiniLM-L6-v2 | Semantic search |

---

## 📋 Requirements

### System Requirements
- **OS**: Windows 10/11, macOS, or Linux
- **RAM**: 8GB minimum (16GB recommended)
- **GPU**: 6GB VRAM for Ollama (optional, CPU works too)
- **Disk**: ~2GB free space

### Software Requirements
- **Node.js**: v18+ (for frontend)
- **Python**: 3.10+ (for backend)
- **Ollama**: Latest version (for LLM)

---

## 🚀 Installation

### Step 1: Install Ollama

Download and install from: https://ollama.ai

```bash
# Verify installation
ollama --version
```

### Step 2: Pull the LLM Model

```bash
ollama pull qwen2.5:7b-instruct
```

### Step 3: Start Ollama Server

```bash
ollama serve
```

### Step 4: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/career-recommender.git
cd career-recommender
```

### Step 5: Setup Backend

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Setup Frontend

```bash
cd frontend
npm install
cd ..
```

### Step 7: Build FAISS Index (Optional)

```bash
python scripts/build_index.py
```

---

## 🎮 Usage

### Start the Backend

```bash
python api_server_v3.py
```

The API server will start at: `http://localhost:8000`

### Start the Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will start at: `http://localhost:5173`

### Access the Application

Open your browser and navigate to: `http://localhost:5173`

---

## 📁 Project Structure

```
career-recommender/
├── api_server_v3.py              # Main FastAPI backend server
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── .gitignore                    # Git ignore rules
│
├── frontend/                     # React + TypeScript frontend
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Page components
│   │   │   ├── Landing.tsx      # Landing page with puzzle
│   │   │   ├── Form.tsx         # Career questionnaire
│   │   │   └── Result.tsx       # Results with roadmap
│   │   ├── hooks/               # Custom React hooks
│   │   ├── types/               # TypeScript type definitions
│   │   ├── App.tsx              # Main app component
│   │   └── main.tsx             # Entry point
│   ├── package.json             # Node.js dependencies
│   ├── vite.config.ts           # Vite configuration
│   ├── tailwind.config.js       # Tailwind CSS config
│   └── tsconfig.json            # TypeScript config
│
├── backend/                      # Backend modules
│   ├── config.py                # Configuration constants
│   ├── schemas.py               # Pydantic data models
│   ├── scoring.py               # Career scoring algorithm
│   ├── rag.py                   # FAISS retrieval
│   ├── llm_engine.py            # Ollama LLM interface
│   └── recommend.py             # Recommendation pipeline
│
├── data/                         # Data files
│   ├── careers.json             # Career definitions
│   ├── synonyms.json            # Skill synonyms
│   └── kb_docs/                 # Knowledge base documents
│
└── scripts/                      # Utility scripts
    └── build_index.py           # Build FAISS index
```

---

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/recommend` | POST | Get career recommendations |
| `/api/roadmap/{career}` | GET | Get career roadmap |
| `/api/news/{career}` | GET | Get career news |
| `/api/chat` | POST | Chat with career advisor |

### Example Request

```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "educationLevel": "Graduate",
    "interests": ["farming", "agriculture", "organic"],
    "skills": ["gardening", "plant care"],
    "hobbies": ["growing vegetables"],
    "personalityTraits": ["hardworking"],
    "extraInfo": "I want to start an organic farm"
  }'
```

---

## 🎨 Color Scheme

| Color | Hex | Usage |
|-------|-----|-------|
| Dark Green | `#1B4D3E` | Primary background, headers |
| Lime | `#C5E500` | Accents, highlights, CTAs |
| White | `#FFFFFF` | Text, cards |
| Light Gray | `#F5F5F5` | Secondary backgrounds |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for local LLM inference
- [FastAPI](https://fastapi.tiangolo.com) for the backend framework
- [React](https://react.dev) for the frontend framework
- [Tailwind CSS](https://tailwindcss.com) for styling
- [Framer Motion](https://www.framer.com/motion/) for animations

---

<div align="center">

**Made with ❤️ for career seekers everywhere**

</div>
