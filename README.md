# ACME Senior Living - Multi-Agent Sales Assistant

A demonstration of a multi-agent AI sales system for senior living communities, built for the Further AI Engineer take-home assignment.

## Project Overview

This system replaces a monolithic prompt-based chatbot with a specialized multi-agent architecture that demonstrates:

- **Functional Decomposition**: 5 specialized agents (Intent Classifier, Pricing, Tour Scheduling, Amenities, General Info)
- **Event-Based Enrichment**: LLM-powered extraction of insights from conversations
- **RAG with pgvector**: Semantic search using OpenAI embeddings and PostgreSQL pgvector
- **LangFuse Observability**: Comprehensive tracing of all agent operations
- **Real-Time Understanding**: Transparent display of what the system learns about prospects

## Architecture

### Backend (Django + LangGraph)
- **Framework**: Django 5.2 with Django REST Framework
- **Package Manager**: uv for fast, reproducible Python dependency management  
- **Multi-Agent Workflow**: LangGraph orchestrates 5 specialized agents
- **RAG**: pgvector for vector similarity search, OpenAI text-embedding-3-small
- **LLM**: GPT-4o-mini for all agent operations
- **Observability**: LangFuse SDK tracing all LLM calls, RAG retrievals, and enrichments
- **Database**: PostgreSQL 16 with pgvector extension

### Frontend (React + Vite)
- **Framework**: React 18 with Vite  
- **Styling**: Tailwind CSS
- **Features**: Chat interface with real-time understanding panel

### Admin Dashboard (React + Vite)
- **Purpose**: View all prospects, conversations, and enrichment events
- **Features**: Detailed conversation history, enrichment timeline, current understanding

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- (Optional) LangFuse account for observability

## Quick Start

1. **Clone the repository**
   ```bash
   cd interview-test
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`: (Optional) Your LangFuse credentials

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

4. **Access the applications**
   - Chat UI: http://localhost:3000
   - Admin Dashboard: http://localhost:3001
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/

## Development Setup

### Backend

```bash
cd backend

# Install uv
pip install uv

# Install dependencies
uv sync

# Run migrations
uv run python manage.py migrate

# Seed knowledge base (requires OPENAI_API_KEY)
uv run python manage.py seed_knowledge

# Run development server
uv run python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Admin Dashboard

```bash
cd admin
npm install
npm run dev
```

## API Endpoints

### Chat
- `POST /api/chat` - Send a message and get agent response

### Admin
- `GET /api/admin/prospects` - List all prospects
- `GET /api/admin/prospects/{id}` - Get prospect details with full conversation history

### Testing
- `POST /api/test/agent/{agent_name}` - Test individual agents in isolation

## Multi-Agent System

### Agent Flow

1. **Intent Classifier**: Categorizes user message into one of 5 intents
2. **Specialized Agent**: Routes to appropriate agent based on intent
   - **Pricing Agent**: Handles cost inquiries with RAG-powered responses
   - **Tour Scheduling Agent**: Manages tour availability and scheduling
   - **Amenities Agent**: Answers questions about facilities and services
   - **General Info Agent**: Fallback for all other questions
3. **Enrichment Extractor**: LLM analyzes conversation to extract enrichment events
4. **Understanding Updater**: Updates real-time understanding based on enrichments

### Enrichment Events

The system automatically extracts and tracks:
- Budget inquiries and mentions
- Care needs expressed (conditions, care levels)
- Timeline information
- Preferences (pets, dietary, amenities)
- Tour interest and scheduling
- Financing inquiries
- Room type interests

## Key Design Decisions

### 1. Event-Based Enrichment
Instead of flattening enrichment data into Prospect fields, events are stored separately and aggregated into `current_understanding`. This provides:
- Full audit trail of learnings
- Ability to track confidence scores
- Flexibility to adjust understanding logic without schema changes

### 2. RAG with pgvector
- Knowledge base seeded from structured JSON (36 ACME facts)
- Embeddings generated using OpenAI text-embedding-3-small (1536 dimensions)
- Semantic search using L2 distance in PostgreSQL
- Category filtering for specialized agents

### 3. LangFuse Observability
- All LLM calls traced with input/output
- RAG retrievals logged with results
- Enrichment extraction tracked
- Session-based tracing for full conversation context

### 4. Simplified for Demo
To meet time constraints, the following were simplified:
- No contact collection flow (would extract from conversation)
- Basic tour scheduling (no CRM integration)
- Simplified prospect model (minimal contact fields)
- No authentication/authorization
- SQLite OK for local dev, but PostgreSQL required for pgvector

## Project Structure

```
interview-test/
├── backend/
│   ├── config/              # Django project settings
│   ├── sales_agent/         # Main Django app
│   │   ├── agents/          # LangGraph workflow
│   │   ├── management/      # Django commands
│   │   ├── models.py        # Database models
│   │   ├── rag.py           # RAG retriever
│   │   ├── views.py         # API endpoints
│   │   └── urls.py          # URL routing
│   ├── data/                # Knowledge base JSON
│   ├── Dockerfile
│   └── pyproject.toml       # Python dependencies
├── frontend/                # React chat UI
│   ├── src/
│   │   ├── components/      # React components
│   │   └── App.jsx          # Main app
│   ├── Dockerfile
│   └── nginx.conf
├── admin/                   # React admin dashboard
│   ├── src/
│   │   ├── components/      # React components
│   │   └── App.jsx          # Main app
│   ├── Dockerfile
│   └── nginx.conf
├── docs/                    # Design documentation
│   ├── tech-design.md       # Technical design
│   └── project-status.md    # Implementation tracker
├── docker-compose.yml
├── .env.example
└── README.md
```

## Testing

### Test Individual Agents

```bash
# Test intent classification
curl -X POST http://localhost:8000/api/test/agent/intent \
  -H "Content-Type: application/json" \
  -d '{"message": "How much does assisted living cost?"}'

# Test pricing agent
curl -X POST http://localhost:8000/api/test/agent/pricing \
  -H "Content-Type: application/json" \
  -d '{"message": "What is included in the monthly cost?"}'

# Test tour scheduling
curl -X POST http://localhost:8000/api/test/agent/tour \
  -H "Content-Type: application/json" \
  -d '{"message": "Can I schedule a tour for Friday?"}'
```

### Test Full Conversation

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "My mom needs assisted living for dementia. What are the costs?"}'
```

## Deployment

### Railway Deployment

1. **Create Railway project**
   ```bash
   railway init
   ```

2. **Add PostgreSQL service**
   ```bash
   railway add postgresql
   ```

3. **Set environment variables**
   ```bash
   railway variables set OPENAI_API_KEY=<your-key>
   railway variables set LANGFUSE_PUBLIC_KEY=<your-key>
   railway variables set LANGFUSE_SECRET_KEY=<your-key>
   ```

4. **Deploy**
   ```bash
   railway up
   ```

## Assumptions and Constraints

### Time Constraints
- Assignment specified 2-3 hours, realistic estimate 21-30 hours
- Focused on demonstrating core capabilities over production polish
- Priority: business value > technical depth > production thinking > UX

### Simplifications
- No user authentication (would use Django's built-in auth + JWT)
- No contact collection flow (would extract from NER in conversation)
- No CRM integration (would sync to Salesforce/HubSpot)
- Basic error handling (would add retry logic, circuit breakers)
- No rate limiting (would add Redis-based rate limiting)

### Production Considerations Not Implemented
- API versioning
- Request/response validation with Pydantic
- Comprehensive test suite (unit, integration, e2e)
- CI/CD pipeline
- Monitoring and alerting
- Database connection pooling
- Caching layer (Redis)
- CDN for static assets

## Technologies Used

- **Backend**: Python 3.11, Django 5.2, Django REST Framework, uv
- **AI/ML**: OpenAI GPT-4o-mini, text-embedding-3-small, LangChain, LangGraph
- **Database**: PostgreSQL 16, pgvector
- **Frontend**: React 18, Vite, Tailwind CSS
- **Observability**: LangFuse
- **Deployment**: Docker, Docker Compose, Railway

## Future Enhancements

1. **Contact Collection**: Extract contact info from conversation using NER
2. **Calendar Integration**: Sync tour bookings with Google Calendar/Outlook
3. **CRM Integration**: Push prospects to Salesforce/HubSpot
4. **Email/SMS**: Send confirmations and follow-ups
5. **Multi-Tenancy**: Support multiple communities
6. **Analytics Dashboard**: Conversion funnels, agent performance metrics
7. **A/B Testing**: Test different agent prompts and flows
8. **Voice Interface**: Integrate with Twilio for phone conversations

## License

This is a demonstration project created for a take-home assignment.
