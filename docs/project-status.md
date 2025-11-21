# Project Status - AI Sales Agent Prototype

**Project**: Further AI Engineer Take-Home Assignment
**Started**: 2025-11-20
**Last Updated**: 2025-11-20
**Target Delivery**: 7 days from assignment receipt

---

## Quick Status

| Component | Status | Progress |
|-----------|--------|----------|
| **Design** | ✅ Complete | 100% |
| **Backend Foundation** | ⏸️ Not Started | 0% |
| **Knowledge Base & RAG** | ⏸️ Not Started | 0% |
| **Multi-Agent System** | ⏸️ Not Started | 0% |
| **Chat UI (Frontend)** | ⏸️ Not Started | 0% |
| **Admin Dashboard** | ⏸️ Not Started | 0% |
| **Deployment** | ⏸️ Not Started | 0% |
| **Documentation** | 🔄 In Progress | 90% |

**Overall Progress**: 10% (Design complete, ready for implementation)

---

## Implementation Checklist

### 🎨 Design & Planning (Complete)
- [x] Tech design document created
- [x] Data models defined (simplified Prospect + event-based enrichment)
- [x] Data flow architecture (domain storytelling format)
- [x] API specifications
- [x] Agent specifications (5 agents: Intent Classifier, Pricing, Tour, Amenities, General Info)
- [x] Real-time understanding summary feature designed
- [x] LLM-based enrichment extraction strategy
- [x] Deployment architecture (Docker + Railway)

### 🏗️ Backend Foundation (Not Started)
**Estimated Time**: 2-3 hours

- [ ] Django project setup with `uv`
  - [ ] Create project structure
  - [ ] Configure `pyproject.toml`
  - [ ] Install dependencies (Django, LangChain, LangGraph, LangFuse, OpenAI, psycopg2, pgvector)
- [ ] PostgreSQL with pgvector setup
  - [ ] Docker Compose configuration
  - [ ] Database initialization
  - [ ] Enable pgvector extension
- [ ] Django models implementation
  - [ ] Prospect model
  - [ ] ConversationSession model
  - [ ] EnrichmentEvent model
  - [ ] CommunityKnowledge model
- [ ] Basic REST API structure
  - [ ] Django REST Framework setup
  - [ ] URL routing
  - [ ] CORS configuration
- [ ] Environment configuration
  - [ ] .env file template
  - [ ] Settings configuration for API keys

**Dependencies**: None
**Blocker**: None

---

### 📚 Knowledge Base & RAG (Not Started)
**Estimated Time**: 1-2 hours

- [ ] Extract ACME facts from `docs/req.md`
  - [ ] Pricing (Step 5)
  - [ ] Amenities (Step 6)
  - [ ] Financing/Medicaid (Step 7)
  - [ ] Policies, room types, contact (Step 12)
  - [ ] All other facts from prompt
- [ ] Create seed script
  - [ ] Parse facts into structured JSON
  - [ ] Generate embeddings with OpenAI
  - [ ] Populate CommunityKnowledge table
- [ ] RAG retrieval function
  - [ ] Vector similarity search with pgvector
  - [ ] Category filtering
  - [ ] Return top-k results with similarity scores

**Dependencies**: Backend Foundation
**Blocker**: None

---

### 🤖 Multi-Agent System (Not Started)
**Estimated Time**: 4-6 hours

#### LangGraph Workflow
- [ ] Define ConversationState TypedDict
- [ ] Create StateGraph workflow
- [ ] Implement routing logic
- [ ] Add workflow nodes
- [ ] Configure edges and conditional routing
- [ ] Compile workflow

#### Intent Classifier Agent
- [ ] Define intent categories
- [ ] Create LLM prompt
- [ ] Implement classification function
- [ ] Test with example messages

#### Pricing Agent
- [ ] Create agent prompt template
- [ ] Implement RAG query for pricing
- [ ] Generate response
- [ ] Extract enrichment events (budget_inquiry, budget_mentioned)
- [ ] Test with pricing questions

#### Tour Scheduling Agent
- [ ] Create date parsing prompt
- [ ] Implement availability checking (mock: Mon-Fri 9am-6pm)
- [ ] Build contact collection flow
- [ ] Create Prospect record
- [ ] Schedule tour
- [ ] Extract enrichment events (tour_requested, tour_scheduled, timeline_shared)
- [ ] Test with tour requests

#### Amenities Agent
- [ ] Create amenities prompt template
- [ ] Implement RAG query for amenities
- [ ] Generate response (2-3 items)
- [ ] Extract enrichment events (preference_stated)
- [ ] Test with amenity questions

#### General Info Agent
- [ ] Create general prompt template
- [ ] Implement broad RAG query
- [ ] Generate response
- [ ] Extract enrichment events (care_need_expressed, financing_inquiry, room_type_interest)
- [ ] Test with various questions

#### Enrichment Event Extraction
- [ ] Create LLM extraction prompt
- [ ] Implement extraction function
- [ ] Handle all event types (budget, care needs, timeline, preferences, tour, financing, room type)
- [ ] Save events to database
- [ ] Test extraction accuracy with req.md examples

#### Real-Time Understanding Updater
- [ ] Implement update logic
- [ ] Map enrichment events to understanding fields
- [ ] Update ConversationSession.current_understanding
- [ ] Test understanding accumulation

**Dependencies**: Backend Foundation, Knowledge Base & RAG
**Blocker**: None

---

### 🔍 LangFuse Integration (Not Started)
**Estimated Time**: 1 hour

- [ ] LangFuse SDK setup
- [ ] Configure API keys
- [ ] Trace intent classification
- [ ] Trace each agent invocation
- [ ] Trace RAG retrieval
- [ ] Trace enrichment extraction
- [ ] Test trace visibility in LangFuse dashboard

**Dependencies**: Multi-Agent System
**Blocker**: Need LangFuse API keys

---

### 💬 Chat UI - Frontend (Not Started)
**Estimated Time**: 3-4 hours

- [ ] React project setup (Vite)
- [ ] Install dependencies (React, Tailwind CSS)
- [ ] Basic chat interface
  - [ ] Message list component
  - [ ] Input box
  - [ ] Send button
  - [ ] Session management
- [ ] Real-Time Understanding Panel
  - [ ] Always-visible display
  - [ ] Budget interest section
  - [ ] Care needs section
  - [ ] Timeline section
  - [ ] Preferences list
  - [ ] Tour interest section
- [ ] API integration
  - [ ] POST /api/chat
  - [ ] Handle session_id
  - [ ] Display responses
  - [ ] Update understanding panel
- [ ] Basic styling
  - [ ] Tailwind CSS setup
  - [ ] Chat bubble design
  - [ ] Understanding panel layout
- [ ] Dockerfile

**Dependencies**: Backend Foundation, Multi-Agent System
**Blocker**: None

---

### 🎛️ Admin Dashboard (Not Started)
**Estimated Time**: 3-4 hours

- [ ] React project setup (Vite) - separate app
- [ ] Install dependencies
- [ ] Prospect List View
  - [ ] Table with columns: Name, Email, Phone, Tour Date, Enrichment Count
  - [ ] Filter by tour_scheduled
  - [ ] Sort by created_at
  - [ ] Click to view details
- [ ] Prospect Detail View
  - [ ] Contact information display
  - [ ] Tour details display
  - [ ] Enrichment Events Timeline
    - [ ] Chronological list
    - [ ] Event type badges
    - [ ] Event data display
    - [ ] Source message display
    - [ ] Timestamp display
  - [ ] Full Conversation History
    - [ ] User messages
    - [ ] Agent responses
    - [ ] Agent names
    - [ ] Timestamps
- [ ] API integration
  - [ ] GET /api/admin/prospects
  - [ ] GET /api/admin/prospects/{prospect_id}
- [ ] Basic styling with Tailwind CSS
- [ ] Dockerfile

**Dependencies**: Backend Foundation, Multi-Agent System
**Blocker**: None

---

### 🧪 Testing & Agent Testing Endpoint (Not Started)
**Estimated Time**: 1-2 hours

- [ ] Create test endpoint: POST /api/test/agent/{agent_name}
- [ ] Test each agent individually
  - [ ] Intent Classifier
  - [ ] Pricing Agent
  - [ ] Tour Scheduling Agent
  - [ ] Amenities Agent
  - [ ] General Info Agent
- [ ] Verify RAG retrieval per agent
- [ ] Verify enrichment extraction per agent
- [ ] Verify LangFuse traces per agent
- [ ] Document test cases

**Dependencies**: Multi-Agent System, LangFuse Integration
**Blocker**: None

---

### 🚀 Deployment (Not Started)
**Estimated Time**: 2-3 hours

- [ ] Docker Compose
  - [ ] Complete docker-compose.yml
  - [ ] Test local deployment
  - [ ] Verify all services start
  - [ ] Test end-to-end flow locally
- [ ] Railway Deployment
  - [ ] Create Railway project
  - [ ] Add PostgreSQL service with pgvector
  - [ ] Deploy backend service
  - [ ] Deploy frontend service
  - [ ] Deploy admin service
  - [ ] Configure environment variables
  - [ ] Test production deployment
- [ ] Domain setup (if applicable)

**Dependencies**: All components
**Blocker**: None

---

### 📝 Documentation & Loom Recording (Not Started)
**Estimated Time**: 2-3 hours

- [ ] README.md
  - [ ] Project overview
  - [ ] Setup instructions (local + Docker)
  - [ ] Environment variables
  - [ ] Running the application
  - [ ] Architecture overview
  - [ ] Assumptions documented
- [ ] API Documentation
  - [ ] Endpoint reference
  - [ ] Request/response examples
- [ ] Loom Recording (5-15 minutes)
  - [ ] Introduction (1-2 min)
  - [ ] Architecture walkthrough (2-3 min)
  - [ ] Live demo - user experience (3-4 min)
  - [ ] Admin dashboard demo (2-3 min)
  - [ ] Technical deep dive (2-3 min)
  - [ ] Business value & next steps (1-2 min)
- [ ] GitHub repository
  - [ ] Clean commit history
  - [ ] Remove sensitive data
  - [ ] Final push

**Dependencies**: All components, Deployment
**Blocker**: None

---

## Session Notes

### Session 1: 2025-11-20 - Design Phase

**Duration**: ~2 hours
**Focus**: Requirements review, design discussion, documentation

**Completed**:
- ✅ Reviewed `docs/req.md` requirements
- ✅ Discussed approach with user
- ✅ Decided on tech stack: Django + React + LangGraph + LangFuse + PostgreSQL (pgvector)
- ✅ Agreed on simplified Prospect model (event-based enrichment)
- ✅ Created `docs/tech-design.md` with:
  - Domain storytelling data flows
  - Simplified data models
  - 5 core agents (Intent Classifier + 4 specialists)
  - Real-time understanding summary feature
  - LLM-based enrichment extraction
  - API specifications
  - Deployment architecture
- ✅ Created `docs/project-status.md` (this file)

**Decisions Made**:
1. **Real-time understanding**: Show all the time (always visible panel)
2. **Enrichment extraction**: Use LLM (simpler than rule-based parsing)
3. **Admin dashboard**: Separate React app (different concern from chat UI)
4. **Agent count**: 5 agents total (1 classifier + 4 specialists)
5. **Skip validation agent**: Focus on RAG accuracy instead
6. **Include LangFuse**: For observability demonstration
7. **Prioritize business value** over technical complexity

**Key Features**:
- Real-time understanding summary panel (transparency feature)
- Event-based enrichment (flexible, auditable)
- Individual agent testing endpoint
- Admin dashboard with enrichment timeline + full conversation history

**Next Session Goal**: Start backend implementation (Django + pgvector setup)

---

## Blockers & Risks

### Current Blockers
- None

### Potential Risks
1. **Time**: 2-3 hour estimate for take-home, need to prioritize ruthlessly
   - **Mitigation**: Focus on Tier 1 features only, skip Tier 2/3 if needed
2. **LangFuse API Keys**: Need credentials for observability
   - **Mitigation**: User mentioned Further will provide OpenAI key, assume LangFuse self-serve signup
3. **pgvector**: Railway may not support pgvector extension
   - **Mitigation**: Verify Railway PostgreSQL supports pgvector, fallback to Supabase if needed
4. **Railway Deployment**: Haven't deployed multi-service app on Railway before
   - **Mitigation**: Test Docker Compose locally first, Railway docs are good

---

## Decisions Log

| Date | Decision | Rationale | Impact |
|------|----------|-----------|--------|
| 2025-11-20 | Use event-based enrichment instead of flattened Prospect attributes | Simpler for prototype, more flexible, easier to audit | Data model simplified, easier to extend |
| 2025-11-20 | 5 agents total (Intent + 4 specialists) instead of 10 | Focus on core functionality, faster implementation | Reduced scope, still demonstrates multi-agent architecture |
| 2025-11-20 | Skip validation agent | RAG with mock data should prevent hallucination | Save time, reduce complexity |
| 2025-11-20 | Include LangFuse integration | Key differentiator for observability | Adds ~1 hour, high value for demo |
| 2025-11-20 | Real-time understanding always visible | Transparency builds trust, unique feature | UI design change, high business value |
| 2025-11-20 | LLM-based enrichment extraction | Simpler than rule-based, more flexible | Easier implementation, better accuracy |
| 2025-11-20 | Separate Admin dashboard app | Different technical concern from chat | More code, but cleaner separation |
| 2025-11-20 | Use `uv` for Python package management | User preference, modern tool | Faster installs |
| 2025-11-20 | PostgreSQL with pgvector instead of FAISS | Production-ready, better for deployment | Slightly more complex setup, better demo |

---

## Time Tracking

| Phase | Estimated | Actual | Status |
|-------|-----------|--------|--------|
| Design & Planning | 2 hours | 2 hours | ✅ Complete |
| Backend Foundation | 2-3 hours | - | ⏸️ Not Started |
| Knowledge Base & RAG | 1-2 hours | - | ⏸️ Not Started |
| Multi-Agent System | 4-6 hours | - | ⏸️ Not Started |
| LangFuse Integration | 1 hour | - | ⏸️ Not Started |
| Chat UI Frontend | 3-4 hours | - | ⏸️ Not Started |
| Admin Dashboard | 3-4 hours | - | ⏸️ Not Started |
| Testing & Debugging | 1-2 hours | - | ⏸️ Not Started |
| Deployment | 2-3 hours | - | ⏸️ Not Started |
| Documentation & Loom | 2-3 hours | - | ⏸️ Not Started |
| **Total** | **21-30 hours** | **2 hours** | **7% Complete** |

**Note**: Original assignment says 2-3 hours time-boxed, but realistically this is a 20-30 hour prototype. Prioritizing demonstrable features over completeness.

---

## Next Steps

### Immediate (Next Session)
1. Backend Foundation
   - Django project setup with `uv`
   - PostgreSQL + pgvector Docker Compose
   - Django models implementation
   - Basic API structure

### After Backend Foundation
2. Knowledge Base Seeding
   - Extract facts from `docs/req.md`
   - Create seed script
   - Populate database

3. Core Agent Implementation
   - Intent Classifier
   - Pricing Agent
   - Test basic workflow

### Future Sessions
- Complete remaining agents
- Build Chat UI
- Build Admin Dashboard
- Deploy to Railway
- Loom recording

---

## Success Criteria

### Must-Have for Demo
- ✅ Multi-agent architecture demonstrated
- ✅ RAG-based responses (no hallucination)
- ✅ Enrichment event capture
- ✅ Real-time understanding panel
- ✅ Admin dashboard with enrichment timeline
- ✅ LangFuse observability
- ✅ Individual agent testing
- ✅ Deployed and accessible

### Nice-to-Have
- Polished UI
- Complete error handling
- All 9 req.md example inputs working perfectly
- Phone call integration (Tier 3 stretch goal)

---

## Questions & Notes

### Questions for User (Answered)
- ✅ Deployment target? → Railway + Docker
- ✅ Multi-agent strategy? → Functional decomposition
- ✅ Differentiation priority? → Business value > Technical depth
- ✅ Frontend scope? → Basic is fine, focus on backend
- ✅ Real-time understanding? → Show all the time
- ✅ Enrichment extraction? → LLM-based
- ✅ Admin dashboard? → Separate React app

### Open Questions
- OpenAI API key: Will Further provide? (req.md says they will)
- LangFuse API key: Self-serve signup or provided?
- Domain for deployment: Use Railway subdomain or custom?

### Notes
- Privacy/security explicitly NOT implemented (documented in tech-design.md)
- Focus on demonstrating capability, not production-readiness
- Mock tour availability (no real calendar integration)
- No CRM integration
- Simplified first-question disclosure flow (no 10-second pause simulation)
