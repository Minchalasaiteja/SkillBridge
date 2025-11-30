# SkillBridge Architecture

## System Overview

SkillBridge implements a sophisticated multi-agent architecture with the following layers:

```
Frontend (HTML/CSS/JS) → Flask API → Multi-Agent System → MongoDB
       ↓                                                      ↓
   Particles.js                                      Persistent Storage
   Animations                                        Session Management
   Responsive                                        Log Collection
```

## Core Components

### 1. Frontend Layer
- **Theme Manager**: Dark/light mode with persistence
- **Navigation Manager**: Smooth scroll navigation
- **Form Manager**: Input collection and API communication
- **Scroll Animation Manager**: Viewport-based animations
- **Particle Background**: Interactive particle effects via particles.js

### 2. Backend Layer (Flask)
- **Health & Status Endpoints**: System monitoring
- **Pathway Generation**: Multi-agent workflow trigger
- **Learner Management**: Profile CRUD operations
- **Session Management**: User session tracking
- **Error Handling**: Comprehensive exception management

### 3. Multi-Agent System

#### Agent Architecture
```
SkillBridgeOrchestrator
  ├─ Goal Analyzer (Sequential)
  │   └─ Analyzes career goals + Gemini insights
  │
  ├─ Resource Researcher (Parallel)
  │   ├─ ThreadPoolExecutor (5 workers)
  │   ├─ Concurrent skill research
  │   └─ Job market analysis
  │
  └─ Roadmap Synthesizer (Loop-based)
      ├─ Iterative drafting (max 3 iterations)
      ├─ Quality evaluation (0-10 scale)
      └─ Threshold: 7.0/10
```

### 4. Database Layer (MongoDB)
- **learner_profiles**: User goal and preferences
- **pathways**: Generated learning pathways
- **sessions**: User session state
- **agent_logs**: Comprehensive execution logs

### 5. Observability Layer
- **Structured Logging**: JSON format with context
- **Execution Tracing**: Operation timing and status
- **Metrics Collection**: Success rates, durations, errors

## Agent Specifications

### Goal Analyzer Agent
- **Input**: Learner preferences
- **Process**: Goal decomposition + Gemini analysis
- **Output**: Goal profile with skills, duration, salary
- **Pattern**: Sequential single agent

### Resource Researcher Agent
- **Input**: Goal profile
- **Process**: Parallel skill research via ThreadPoolExecutor
- **Output**: Matched resources + market insights
- **Pattern**: Parallel execution with 5 worker threads

### Roadmap Synthesizer Agent
- **Input**: Research output
- **Process**: Iterative drafting and evaluation (loop-based)
- **Output**: Multi-phase roadmap with quality score
- **Pattern**: Loop-based with max 3 iterations

## Data Models

### Learner Profile
```
{
  learner_id: String,
  career_goal: String,
  current_skills: [String],
  constraints: [String],
  learning_style: [String],
  time_available_weekly: Int,
  gemini_insights: String,
  created_at: Date
}
```

### Pathway
```
{
  learner_id: String,
  roadmap: {
    pathway_title: String,
    phases: [Phase],
    total_hours: Int
  },
  evaluation_score: Float,
  job_market_insights: Object,
  created_at: Date
}
```

## Key Design Patterns

1. **Singleton Pattern**: MongoDBConnection, ObservabilityManager
2. **DAO Pattern**: LearnerProfile, Pathway, Session, AgentLog
3. **Decorator Pattern**: @require_auth, @app.errorhandler
4. **Observer Pattern**: IntersectionObserver for animations
5. **Strategy Pattern**: Different agent evaluation strategies

## Configuration Management

- **Pydantic Settings**: Type-safe configuration
- **.env File**: Environment-specific values
- **Validation**: Automatic type checking
- **Flexibility**: Multiple environment support

## API Routes

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/generate_pathway | Multi-agent pathway generation |
| GET | /api/health | System health check |
| GET | /api/status | Component status |
| POST | /api/learners | Create learner profile |
| GET | /api/learners/<id> | Retrieve learner |
| PUT | /api/learners/<id> | Update learner |
| GET | /api/pathways/<id> | Get learner pathway |
| GET | /api/observability/summary | Observability data |

## Execution Flow

```
1. User submits form
2. JavaScript validates input
3. POST /api/generate_pathway
4. Orchestrator.generate_pathway()
   ├─ Goal Analyzer runs
   ├─ Resource Researcher runs (parallel)
   └─ Roadmap Synthesizer runs (iterative)
5. Results saved to MongoDB
6. Response returned to frontend
7. Results displayed with animations
```

## Features Implemented

### Multi-Agent System ✅
- [x] Agent powered by LLM (Gemini)
- [x] Parallel agents (Resource Researcher)
- [x] Sequential agents (Orchestrator)
- [x] Loop agents (Roadmap Synthesizer)

### Tools ✅
- [x] Gemini API integration
- [x] Custom tools (Goal analysis, evaluation)
- [x] Built-in tools (ThreadPoolExecutor)

### Sessions & Memory ✅
- [x] Session management
- [x] Long-term memory (MongoDB)
- [x] State management

### Observability ✅
- [x] Structured logging (JSON)
- [x] Execution tracing
- [x] Metrics collection

### Deployment Ready ✅
- [x] Production error handling
- [x] Comprehensive API documentation
- [x] Database persistence
- [x] Modern responsive frontend

## Technologies Used

**Backend**:
- Python 3.9+
- Flask 3.0
- MongoDB 4.6
- Google Generative AI
- OpenTelemetry
- Pydantic

**Frontend**:
- HTML5
- CSS3 with animations
- JavaScript ES6+
- Particles.js
- IntersectionObserver API

## Performance Characteristics

- **Pathway Generation**: < 10 seconds (depends on Gemini latency)
- **Parallel Research**: ~5 concurrent skill researches
- **Database**: Indexed queries for O(1) access
- **Frontend**: 60 FPS animations (hardware-accelerated)

## Security Measures

1. Environment variable protection
2. CORS configuration
3. Input validation (Pydantic)
4. Error sanitization
5. Session management
6. Database connection pooling

## Scalability

- Stateless Flask application
- MongoDB connection pooling
- Configurable worker threads
- Horizontal scaling ready
- CDN-compatible static files

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: November 2024
