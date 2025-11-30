**Title:** SkillBridge — AI Multi-Agent Career Pathway Builder

**Subtitle:** Automated, personalized learning pathways using Google Gemini and MongoDB

**Writeup (<=1500 words):**
- **Introduction (approx 150 words):**
  - Problem: Job-seekers and career switchers struggle to find curated, up-to-date, practical learning pathways tailored to their background, time, and target role.
  - Solution: SkillBridge is a multi-agent system that analyzes career goals, researches high-quality learning resources across platforms, and synthesizes a pragmatic, project-focused roadmap. It uses Google Gemini for reasoning and generation, MongoDB for scalable memory and session persistence, and OpenTelemetry for production-grade observability.

- **System Design (approx 300 words):**
  - Multi-agent architecture: Goal Analyzer decomposes user goals into skills; Resource Researcher searches and ranks courses; Roadmap Synthesizer assembles a step-by-step learning plan with projects and milestones. An orchestrator coordinates agents and manages iteration.
  - Data & persistence: Resources and learner profiles persist in MongoDB. The resource catalog is seeded with 500+ curated entries and supports filtering by topic, level, and time-to-complete.
  - Security & privacy: JWT-based auth protects user endpoints and enables personal long-term memory. Secrets are stored in environment variables.
  - Observability: Structured JSON logs, tracing via Jaeger, and Prometheus metrics provide visibility into agent performance and user workflows.

- **Implementation Highlights (approx 400 words):**
  - Gemini integration: Agents call Gemini for complex decomposition and plan synthesis. Prompts are designed for chain-of-thought style reasoning with temperature control and token limits.
  - Parallel research: ResourceResearcher uses a ThreadPool to query multiple data sources in parallel, enriching candidates with metadata and estimated time-to-complete.
  - Roadmap synthesis loop: The synthesizer drafts an initial plan, evaluates it with the evaluator agent (internal scoring), and iterates to improve practicality and coverage.
  - Database seeding: A `seeder.py` script programmatically generates 500 realistic course/resource entries (providers, topics, durations, URLs, tags) for offline testing and demo purposes. In production one would replace with curated dataset or ingest from APIs.
  - Auth & endpoints: `flask-jwt-extended` secures endpoints; registration/login endpoints issue access tokens; protected APIs accept JWT or session fallback for demo convenience.
  - Observability: `otel_setup.py` configures Jaeger exporter and Prometheus metric reader; Flask and outbound HTTP requests are instrumented.

- **Usage & Demo (approx 200 words):**
  - Setup: populate `.env` with Gemini key and MongoDB URI, install requirements, run `python seeder.py --count 500 --commit` to seed resources, and start the app.
  - Demonstration: Web UI allows users to enter a career goal and background; the system returns a graded, step-by-step pathway with recommended courses and projects.
  - Evaluation: Pathways include an `evaluation_score` and rationale explaining choices, enabling easy human review and iteration.

- **Limitations & Next Steps (approx 150 words):**
  - Limitations: The demo seeder synthesizes resources; real-world production should ingest curated content and periodically refresh metadata. Gemini usage depends on API quotas and costs which should be accounted for. Telemetry exporters may need configuration adjustments to integrate to hosted Jaeger/Prometheus services.
  - Next steps: Add CI, unit tests, richer user roles (mentors), dataset of real course metadata, and automated retriever pipelines to maintain freshness.

**Thumbnail suggestions:**
- Clean modern illustration of a roadmap with nodes (learning steps) and an AI brain icon.
- Screenshot of the UI showing a generated pathway (annotate with callouts about projects and time-to-complete).
- A simple composited thumbnail: a laptop, a roadmap, and the Gemini logo.

**Video script (90-120s):**
- Intro (10s): "Meet SkillBridge — your AI-powered learning roadmap builder for career change and upskilling."
- Problem (10s): "Finding the right, practical set of courses and projects is time-consuming and noisy."
- How it works (30s): "Tell SkillBridge your goal. Our multi-agent system analyzes, researches, and synthesizes a step-by-step pathway with curated resources and projects. We use Google Gemini for reasoning, MongoDB to persist memory, and observability so you can trust results."
- Demo (30s): "Here’s a 60-second demo: enter 'Become a Machine Learning Engineer', pick your background, and receive a graded roadmap with projects, timelines, and recommended courses."
- Call to action (10s): "Try the demo, review the generated roadmap, and contribute your favorite resources to improve results."
