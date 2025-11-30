# SkillBridge: AI-Powered Career Pathway Generator
## Agents Intensive Capstone Project

### 🎯 Project Overview

**SkillBridge** is an enterprise-grade multi-agent AI system that leverages Google's Gemini API to generate personalized learning pathways for career development. This capstone project demonstrates advanced AI agent architecture with parallel processing, iterative evaluation, and comprehensive observability.

**Track:** Concierge Agents  
**Problem Statement:** Career planning is too manual and resource-intensive. SkillBridge automates and personalizes the learning journey, saving users 10+ hours of research and planning.

---

## 🏆 Key Features

### Multi-Agent Architecture
- **Goal Analyzer Agent**: Decomposes career aspirations using Gemini AI
- **Resource Researcher Agent**: Parallel search across learning platforms
- **Roadmap Synthesizer Agent**: Iterative optimization with quality evaluation

### Advanced Capabilities
✅ **Parallel Agent Execution** - ThreadPoolExecutor for concurrent resource research  
✅ **Sequential Orchestration** - Coordinated multi-step workflow  
✅ **Loop-Based Evaluation** - Self-improving roadmap generation  
✅ **Gemini Integration** - Advanced LLM insights and analysis  
✅ **MongoDB Persistence** - Long-term memory with database storage  
✅ **Observability Suite** - Logging, tracing, and metrics collection  
✅ **Session Management** - InMemorySessionService for state tracking  
✅ **Enterprise API** - RESTful endpoints with error handling  
✅ **Modern UI/UX** - Particle effects, animations, responsive design  

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.0.0
- **AI/LLM**: Google Generative AI (Gemini)
- **Database**: MongoDB 4.6
- **Async**: ThreadPoolExecutor, asyncio
- **Logging**: OpenTelemetry, JSON logging
- **Config**: pydantic-settings with .env

### Frontend
- **HTML5** with semantic markup
- **CSS3** with modern features (gradients, animations, particles)
- **JavaScript (ES6+)** with class-based architecture
- **Particles.js** for background effects
- **Responsive Design** - Mobile-first approach

---

## 📋 Project Structure

```
skillbridge/
├── .env.example              # Environment configuration template
├── config.py                 # Configuration management (Pydantic)
├── database.py              # MongoDB models and operations
├── agents.py                # Multi-agent system implementation
├── observability.py         # Logging, tracing, metrics
├── app.py                   # Flask API endpoints
├── index.html              # Modern frontend interface
├── style.css               # Advanced CSS with animations
├── script.js               # Interactive JavaScript with particles
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- MongoDB 4.6+ (local or cloud instance)
- Google Gemini API key

### Installation

1. **Create .env file from template**
```bash
cp .env.example .env
```

2. **Update .env with your credentials**
```
GEMINI_API_KEY=your_api_key_here
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/skillbridge
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Access the application**
- API: http://localhost:5000
- Frontend: Open index.html in browser

---

## 📡 API Endpoints

### Pathway Generation
```
POST /api/generate_pathway
```

### Learner Profile
```
POST /api/learners
GET /api/learners/<learner_id>
PUT /api/learners/<learner_id>
```

### Health & Status
```
GET /api/health
GET /api/status
GET /api/observability/summary
```

---

## 🤖 Agent Architecture

### Goal Analyzer Agent
Decomposes career goals using Gemini AI analysis

### Resource Researcher Agent
Parallel search across learning platforms

### Roadmap Synthesizer Agent
Iterative roadmap generation with quality evaluation

---

## 💾 Data Persistence

**MongoDB Collections:**
- `learner_profiles` - User goal and preference storage
- `pathways` - Generated learning pathways
- `sessions` - User session management
- `agent_logs` - Comprehensive agent execution logs

---

## 🎨 Frontend Features

✨ **Dark/Light Mode** - Theme toggle with persistence  
✨ **Particle Background** - Interactive particle effects  
✨ **Smooth Animations** - CSS keyframes and transitions  
✨ **Responsive Design** - Works on all devices  
✨ **Real-time Updates** - Dynamic form handling  

---

## 🔧 Configuration

All configuration via `.env` file using Pydantic validation:

```bash
FLASK_ENV=development
GEMINI_API_KEY=your_api_key
MONGODB_URI=your_mongodb_uri
LOG_LEVEL=INFO
ENABLE_TRACING=True
```

---

## 📈 Evaluation Metrics

Pathways evaluated on:
1. Goal Alignment (2.5/10)
2. Feasibility (2.5/10)
3. Certification Value (1.0/10)
4. Quality (2.0/10)
5. Accessibility (1.0/10)

**Threshold**: 7.0/10 for approval

---

## 🎓 Supported Career Goals

- Data Scientist
- Data Analyst
- Web Developer
- Cloud Engineer
- AI/ML Engineer

---

## 🔐 Security

✅ Environment variable configuration  
✅ API validation with Pydantic  
✅ CORS protection  
✅ Session management  
✅ Structured audit logging  

---

## 📚 Key Implementations

### Multi-Agent System
- Sequential orchestration
- Parallel agent execution
- Loop-based iteration
- State management

### Observability
- Structured JSON logging
- Execution tracing
- Metrics collection
- Error aggregation

### Database
- MongoDB persistence
- Connection pooling
- Schema validation
- Index optimization

---

## 🚀 Production Ready

✅ Error handling and recovery  
✅ Input validation  
✅ Database connection management  
✅ API documentation  
✅ Logging and monitoring  
✅ Responsive frontend  
✅ Performance optimized  

---

## 📄 License

Part of Kaggle Agents Intensive Capstone Program

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Updated**: November 2024
