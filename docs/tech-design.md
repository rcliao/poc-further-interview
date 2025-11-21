# AI Sales Agent - Technical Design Document

**Version**: 1.0
**Last Updated**: 2025-11-20
**Status**: Ready for Implementation

---

## 1. System Overview

Multi-agent AI sales assistant for ACME Senior Living that replaces a monolithic prompt with specialized, testable, and monitorable agents.

### Design Principles
- **Functional decomposition**: Each agent handles one business capability
- **Event-based enrichment**: Capture learnings as events, not flattened attributes
- **Observable**: Every decision traced via LangFuse
- **Transparent**: Real-time understanding summary shown to users
- **Testable**: Individual agents can be tested in isolation

### Business Goals
1. **Accuracy**: Specialist agents provide more accurate responses than monolithic prompt
2. **No Hallucination**: RAG ensures responses based on verified facts
3. **Transparency**: Users see what the agent understands in real-time
4. **Monitoring**: LangFuse enables observability and debugging
5. **Qualification**: Enrichment events provide sales context for tours

---

## 2. Data Flow Architecture (Domain Storytelling)

### Actors
- **Prospect**: Person inquiring about ACME Senior Living
- **Chat API**: Receives and routes incoming messages
- **Intent Classifier**: Determines what the prospect is asking about
- **Workflow Router**: Directs conversation to appropriate specialist agent
- **Specialist Agents**: Domain experts (Pricing, Tour Scheduling, Amenities, General Info)
- **Knowledge Base**: PostgreSQL with pgvector containing community facts
- **Understanding Updater**: Maintains real-time summary of conversation context
- **Enrichment Extractor**: Identifies and logs learnings from conversation
- **Observability System**: LangFuse tracing and monitoring

### Work Objects
- **Message**: Text from prospect or agent
- **Conversation State**: Session data, history, current understanding
- **Intent Classification**: Categorized user request
- **Knowledge Context**: Retrieved facts from vector database
- **Agent Response**: Generated answer from specialist agent
- **Current Understanding**: Real-time summary of what agent has learned
- **Enrichment Event**: Specific learning extracted from conversation
- **Trace**: LangFuse record of agent decisions

---

### Story 1: First-Time Pricing Inquiry with Real-Time Understanding

**Scenario**: Prospect asks about community costs for the first time

1. **Prospect** sends **message** "How much does it cost?" to **Chat API**
2. **Chat API** creates new **conversation state** with session ID
3. **Chat API** forwards **message** + **conversation state** to **Intent Classifier**
4. **Intent Classifier** analyzes **message** and produces **intent classification**: "pricing"
5. **Workflow Router** routes to **Pricing Agent**
6. **Pricing Agent** queries **Knowledge Base** with "pricing information"
7. **Knowledge Base** performs vector search and returns **knowledge context** (pricing facts)
8. **Pricing Agent** generates **agent response** using **knowledge context**
9. **Enrichment Extractor** analyzes **message** + **agent response**
10. **Enrichment Extractor** creates **enrichment event**: type="budget_inquiry", data="interested in pricing"
11. **Understanding Updater** updates **current understanding**: budget_interest = "$2000+ range"
12. **Observability System** logs **trace** to LangFuse (intent classification, RAG retrieval, response generation)
13. **Chat API** returns **agent response** + **current understanding** to **Prospect**

**Result**:
- Prospect receives: "Our community starts at $2000/month for Independent Living, $3000/month for Assisted Living..."
- **Real-time understanding panel shows**: "Budget Interest: $2000+ pricing range"

---

### Story 2: Enrichment Event Extraction

**Scenario**: Prospect shares care needs and preferences

1. **Prospect** sends **message** "My mom is 82, has dementia, and we need her to move in quickly. She has a golden retriever she loves."
2. **Intent Classifier** produces **intent classification**: "general_info" (care types)
3. **General Info Agent** queries **Knowledge Base** for care types and pet policy
4. **General Info Agent** generates **agent response** about Assisted Living and pet policy
5. **Enrichment Extractor** analyzes **message** using LLM extraction
6. **Enrichment Extractor** creates multiple **enrichment events**:
   - Event 1: type="care_need_expressed", data={"condition": "dementia", "care_level": "assisted_living"}
   - Event 2: type="timeline_shared", data={"urgency": "immediate", "context": "need to move quickly"}
   - Event 3: type="preference_stated", data={"category": "pets", "detail": "golden retriever"}
7. **Understanding Updater** updates **current understanding**:
   - care_needs = ["Assisted Living", "Memory care support"]
   - timeline = "Immediate move needed"
   - preferences = ["Pet: golden retriever (note: large dog policy check needed)"]
8. **Observability System** logs **trace** including all enrichment events extracted
9. **Chat API** returns response with updated **current understanding** panel

**Result**:
- Prospect sees comprehensive answer about care + pet policy
- **Real-time understanding panel shows**:
  ```
  Care Needs: Assisted Living, Memory support
  Timeline: Immediate
  Preferences: Pet - golden retriever
  ```

---

### Story 3: Tour Scheduling with Contact Collection

**Scenario**: Prospect wants to schedule a tour

1. **Prospect** sends **message** "I'd like to schedule a tour for next Sunday at 3pm"
2. **Intent Classifier** produces **intent classification**: "tour_scheduling"
3. **Tour Scheduling Agent** queries **Knowledge Base** for "tour availability hours"
4. **Knowledge Base** returns **knowledge context**: "Monday-Friday, 9am-6pm"
5. **Tour Scheduling Agent** parses requested date: "Sunday 3pm"
6. **Tour Scheduling Agent** checks availability: Sunday NOT in Monday-Friday
7. **Tour Scheduling Agent** generates **agent response** with conflict + alternative: "We're open Monday-Friday, 9am-6pm. Does Tuesday at 2pm work?"
8. **Enrichment Extractor** creates **enrichment event**: type="tour_requested", data={"requested": "Sunday 3pm", "available": false}
9. **Understanding Updater** updates **current understanding**: tour_interest = "High - requested specific time"
10. **Prospect** replies "Yes, Tuesday at 2pm works"
11. **Tour Scheduling Agent** asks for contact info: "Great! Can I get your first name?"
12. **Prospect** provides: "James" → "Smith" → "james@email.com" → "555-1234"
13. **Tour Scheduling Agent** creates **Prospect** record with contact info
14. **Tour Scheduling Agent** schedules tour for Tuesday 2pm
15. **Enrichment Extractor** creates **enrichment event**: type="tour_scheduled", data={"datetime": "2025-03-10T14:00:00Z"}
16. **Chat API** returns confirmation to **Prospect**

**Result**:
- Tour scheduled, prospect record created
- Admin dashboard shows new prospect with enrichment events

---

### Story 4: Admin Reviews Prospect Before Tour

**Scenario**: Community manager prepares for James Smith's tour

1. **Community Manager** opens **Admin Dashboard**
2. **Admin Dashboard** displays **Prospect List** with James Smith (tour scheduled for Mar 10, 2pm)
3. **Community Manager** clicks on James Smith
4. **Admin Dashboard** shows **Prospect Detail View**:
   - Contact: James Smith, james@email.com, 555-1234
   - Tour: Tuesday, March 10, 2pm
   - **Enrichment Timeline**:
     - 10:30 AM - budget_inquiry: "Interested in pricing"
     - 10:31 AM - financing_inquiry: "Asked about Medicaid"
     - 10:33 AM - care_need_expressed: "Mother has dementia, needs assisted living"
     - 10:34 AM - preference_stated: "Pet: golden retriever (large dog - policy conflict)"
     - 10:35 AM - preference_stated: "Dietary: Kosher, low sodium"
     - 10:40 AM - tour_requested: "Wants to visit"
     - 10:42 AM - tour_scheduled: "Tuesday March 10, 2pm"
   - **Full Conversation History**: [entire transcript]
5. **Community Manager** reviews context and prepares:
   - Mother needs memory care support
   - Medicaid financing interest (discuss payment options)
   - Golden retriever = 50+ lbs (exceeds 25 lb limit - prepare alternative solutions)
   - Dietary needs: Kosher + low sodium (confirm kitchen can accommodate)

**Result**:
- Manager enters tour with full context
- Can address specific concerns proactively
- Better conversion rate

---

## 3. Data Models

### 3.1 Prospect (Simplified)
```python
class Prospect(models.Model):
    """
    Represents a person inquiring about ACME Senior Living
    Minimal model - enrichment stored as events, not flattened attributes
    """
    prospect_id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # Contact Info (collected during tour scheduling)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)

    # Tour Details
    tour_scheduled = models.BooleanField(default=False)
    tour_datetime = models.DateTimeField(null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tour_scheduled']),
        ]
```

### 3.2 ConversationSession
```python
class ConversationSession(models.Model):
    """
    Represents a single chat session with a prospect
    A prospect can have multiple sessions over time
    """
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    prospect = models.ForeignKey(
        Prospect,
        on_delete=models.CASCADE,
        null=True,
        related_name='sessions'
    )

    # Conversation history
    conversation_history = models.JSONField(default=list)
    # [
    #   {
    #     "role": "user",
    #     "content": "How much does it cost?",
    #     "timestamp": "2025-03-04T10:30:00Z"
    #   },
    #   {
    #     "role": "assistant",
    #     "content": "Our community starts at $2000/month...",
    #     "agent": "pricing_agent",
    #     "timestamp": "2025-03-04T10:30:02Z"
    #   }
    # ]

    # Real-time understanding (displayed to user for transparency)
    current_understanding = models.JSONField(default=dict)
    # {
    #   "budget_interest": "$2000-$3000 range",
    #   "care_needs": ["Assisted Living", "Memory care support"],
    #   "timeline": "Immediate move needed",
    #   "preferences": ["Pet: golden retriever", "Dietary: Kosher, low sodium"],
    #   "tour_interest": "High - requested specific time"
    # }

    # Session metadata
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-started_at']
```

### 3.3 EnrichmentEvent
```python
class EnrichmentEvent(models.Model):
    """
    Captures specific learnings from conversation
    Event-based approach: easier to track, audit, and extend
    """
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    session = models.ForeignKey(
        ConversationSession,
        on_delete=models.CASCADE,
        related_name='enrichment_events'
    )

    # Event type based on req.md examples
    event_type = models.CharField(max_length=50)
    # Types:
    # - budget_inquiry: User asked about pricing
    # - budget_mentioned: User stated specific budget range
    # - care_need_expressed: User mentioned care needs (dementia, mobility, etc.)
    # - timeline_shared: User indicated urgency or move timeline
    # - preference_stated: User mentioned preferences (pets, dietary, amenities, etc.)
    # - tour_requested: User wants to visit
    # - tour_scheduled: Tour confirmed with date/time
    # - financing_inquiry: User asked about payment options (Medicaid, etc.)
    # - room_type_interest: User asked about specific room types

    # Event data (flexible JSON structure)
    event_data = models.JSONField()
    # Examples:
    # budget_mentioned: {"range": "$3000-$4000", "flexibility": "flexible"}
    # care_need_expressed: {"condition": "dementia", "care_level": "assisted_living"}
    # preference_stated: {"category": "pets", "detail": "golden retriever"}
    # timeline_shared: {"urgency": "immediate", "context": "hospital discharge"}

    # Extraction metadata
    extracted_by_agent = models.CharField(max_length=100)
    source_message = models.TextField()  # User message that triggered extraction
    confidence = models.FloatField(default=1.0)  # 0.0-1.0

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['event_type']),
        ]
```

### 3.4 CommunityKnowledge (RAG)
```python
class CommunityKnowledge(models.Model):
    """
    Knowledge base for RAG retrieval
    Contains all ACME Senior Living facts from req.md
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    category = models.CharField(max_length=50)
    # Categories: pricing, amenities, services, policies, activities,
    #             care_types, room_types, financing, contact, dietary

    content = models.TextField()  # Human-readable fact
    metadata = models.JSONField()  # Structured data for filtering
    embedding = VectorField(dimensions=1536)  # pgvector for similarity search

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['category']),
        ]
```

**Example Knowledge Entries:**

```json
// Pricing
{
  "category": "pricing",
  "content": "Independent Living starts from $2000 a month. Assisted Living starts from $3000 a month. Entrance fee is $3500. Monthly cost includes: Basic Cable, Internet/WiFi, Linen Service, Breakfast, Lunch, Dinner, Housekeeping.",
  "metadata": {
    "independent_living_base": 2000,
    "assisted_living_base": 3000,
    "entrance_fee": 3500,
    "included": ["cable", "internet", "linen", "meals", "housekeeping"]
  }
}

// Pet Policy
{
  "category": "policies",
  "content": "Pets are allowed: Cats allowed, Small dogs allowed (under 25 lbs), Service animals allowed, Fishes, Small birds",
  "metadata": {
    "pets_allowed": true,
    "allowed_pets": ["cats", "small_dogs_under_25lbs", "service_animals", "fish", "small_birds"],
    "weight_limit_dogs": 25
  }
}

// Dietary Options
{
  "category": "dietary",
  "content": "Dietary options available: Diabetic options, Low sugar/salt, Vegetarian, Gluten-free. Note: We do not have information about Kosher meal preparation.",
  "metadata": {
    "dietary_options": ["diabetic", "low_sugar", "low_salt", "vegetarian", "gluten_free"]
  }
}
```

---

## 4. Agent Specifications

### 4.1 Intent Classifier Agent

**Purpose**: Route user message to appropriate specialist agent

**Input**:
- User message
- Conversation history (last 3 messages for context)

**Output**: Intent classification

**Categories**:
- `pricing` - Questions about cost, fees, monthly rates
- `tour_scheduling` - Wants to visit, schedule tour
- `amenities` - Questions about facilities, services, activities
- `financing` - Medicaid, HUD, insurance, payment options
- `general_info` - Contact, policies, room types, care types, everything else

**LLM Prompt**:
```
You are an intent classifier for a senior living sales assistant.

Classify the user's intent into ONE category:
- pricing: Cost, fees, monthly rates, what's included in price
- tour_scheduling: Schedule tour, visit, see the community
- amenities: Facilities, services, activities, dining, what's available
- financing: Medicaid, insurance, payment options, financial assistance
- general_info: Everything else (contact info, policies, room types, care types, etc.)

User message: {user_message}
Recent context: {conversation_history}

Return ONLY the category name, nothing else.
```

---

### 4.2 Pricing Agent

**Purpose**: Answer questions about costs and what's included

**Maps to**: Step 5 from req.md

**Input**:
- User message
- Conversation state
- RAG-retrieved pricing knowledge

**Responsibilities**:
1. Query RAG for pricing information
2. Generate response about costs
3. Extract budget-related enrichment events
4. Suggest tour scheduling after answering

**LLM Prompt**:
```
You are Sophie, a sales specialist at ACME Senior Living.

Answer the user's pricing question using ONLY the facts provided below.

Pricing Information:
{rag_retrieved_knowledge}

Guidelines:
- Be warm and conversational
- Only state facts from the knowledge base above
- If asked about specific room pricing you don't have, say: "Pricing varies by room type and care level. I'd recommend scheduling a tour for detailed pricing."
- After answering, suggest scheduling a tour
- Keep response to 2-3 sentences maximum

Conversation history: {conversation_history}
User's question: {user_message}

Your response:
```

**Enrichment Extraction**:
After generating response, call enrichment extractor with:
```
Extract enrichment events from this conversation:

User: {user_message}
Agent response: {agent_response}

Identify and return:
- budget_inquiry: If user asked about pricing (always true for this agent)
- budget_mentioned: If user stated specific budget range
  Example: "That's too expensive, I only have $2500" → budget_mentioned: {"max": 2500, "concern": "affordability"}
```

---

### 4.3 Tour Scheduling Agent

**Purpose**: Schedule tours and collect contact information

**Maps to**: Steps 2-3 from req.md

**Input**:
- User message
- Conversation state
- RAG-retrieved tour availability

**Responsibilities**:
1. Parse requested date/time from user message
2. Check availability (mock: Mon-Fri 9am-6pm)
3. Suggest alternatives if conflict
4. Collect contact info (first name, last name, email, phone)
5. Create Prospect record
6. Schedule tour

**LLM Prompt (Date Parsing)**:
```
You are a tour scheduling specialist at ACME Senior Living.

Tour Availability:
{rag_retrieved_knowledge}

Current date: Tuesday, March 04, 2025, 5:40 AM

User wants to schedule a tour. Parse their requested date and time.

User message: {user_message}

If available, confirm the tour.
If not available (e.g., weekend, outside 9am-6pm, Monday-Friday only), suggest the nearest available alternative.

Be conversational and helpful. Keep response to 2-3 sentences.

Your response:
```

**Contact Collection Flow**:
1. Once date confirmed, ask: "Great! Can I get your first name?"
2. Then: "And your last name?"
3. Then: "What's your email address?"
4. Then: "And a phone number where we can reach you?"
5. Create Prospect record, schedule tour

**Enrichment Extraction**:
```
- tour_requested: User expressed interest in visiting
- tour_scheduled: Tour confirmed with date/time
- timeline_shared: If user mentioned urgency ("soon", "this week", "asap")
```

---

### 4.4 Amenities Agent

**Purpose**: Answer questions about community features, services, activities

**Maps to**: Step 6 from req.md

**Input**:
- User message
- Conversation state
- RAG-retrieved amenities knowledge

**Responsibilities**:
1. Query RAG for relevant amenities/services/activities
2. List 2-3 items from requested category
3. Extract preference-related enrichment events
4. Suggest tour if haven't already

**LLM Prompt**:
```
You are Sophie, a specialist in community amenities at ACME Senior Living.

Answer the user's question using ONLY the facts below.

Available Information:
{rag_retrieved_knowledge}

Guidelines:
- List 2-3 specific items from the category they asked about
- If they ask about something not in the list, say: "I don't have specific information about that, but I can connect you with our team to find out."
- Be enthusiastic but factual
- Keep response to 2-3 sentences

User's question: {user_message}

Your response:
```

**Enrichment Extraction**:
```
- preference_stated: Extract specific preferences mentioned
  Examples:
  - User asks about "air conditioning" → preference_stated: {"category": "room_amenities", "detail": "individual AC control"}
  - User asks about "vegetarian meals" → preference_stated: {"category": "dietary", "detail": "vegetarian"}
  - User asks about "pets" → preference_stated: {"category": "pets", "detail": <extract pet type from context>}
```

---

### 4.5 General Info Agent

**Purpose**: Fallback for all other questions (contact, policies, care types, room types, etc.)

**Maps to**: Steps 7, 10, 11, 12, 19, 20 from req.md

**Input**:
- User message
- Conversation state
- RAG-retrieved knowledge (any category)

**Responsibilities**:
1. Query RAG with broad search
2. Provide best-match answer
3. Extract care-needs or other enrichment events
4. Offer to connect with human if can't answer

**LLM Prompt**:
```
You are Sophie, a sales specialist at ACME Senior Living.

Answer the user's question using ONLY the facts below.

Available Information:
{rag_retrieved_knowledge}

Guidelines:
- Use the provided facts to answer
- If the knowledge base doesn't contain the answer, say: "I don't have specific information about that. Would you like me to connect you with our team?"
- Be warm and helpful
- Keep response to 2-3 sentences

User's question: {user_message}

Your response:
```

**Enrichment Extraction**:
```
- care_need_expressed: Extract any care needs, medical conditions, or care level indicators
  Examples:
  - "My mom has dementia" → care_need_expressed: {"condition": "dementia", "care_level": "memory_care"}
  - "She needs help with bathing" → care_need_expressed: {"assistance": "bathing", "care_level": "assisted_living"}

- financing_inquiry: Extract payment method questions
  Examples:
  - "Do you take Medicaid?" → financing_inquiry: {"type": "medicaid"}
  - "What about Veterans benefits?" → financing_inquiry: {"type": "veterans_benefits"}

- room_type_interest: Extract room type preferences
  Examples:
  - "How much for a 2 bedroom?" → room_type_interest: {"type": "2_bedroom"}
```

---

## 5. Enrichment Event Extraction

### 5.1 LLM-Based Extraction

After each agent response, call enrichment extractor:

**Extraction Prompt**:
```
You are an enrichment event extractor for a senior living sales conversation.

Analyze the user's message and identify any enrichment events.

User message: "{user_message}"
Agent response: "{agent_response}"
Agent type: "{agent_name}"

Extract events in JSON format:

Event types:
- budget_inquiry: User asked about pricing
- budget_mentioned: User stated specific budget (extract amount/range)
- care_need_expressed: User mentioned care needs, conditions, or assistance required
- timeline_shared: User indicated urgency or move timeline
- preference_stated: User mentioned preferences (pets, dietary, amenities, couples, etc.)
- tour_requested: User expressed interest in visiting
- tour_scheduled: Tour confirmed with date/time
- financing_inquiry: User asked about payment options (Medicaid, insurance, etc.)
- room_type_interest: User asked about specific room types

Return JSON array:
[
  {
    "event_type": "care_need_expressed",
    "event_data": {
      "condition": "dementia",
      "care_level": "assisted_living"
    },
    "source_message": "My mom has dementia",
    "confidence": 0.95
  }
]

If no enrichment events found, return empty array: []
```

### 5.2 Enrichment Event Examples (from req.md)

| User Message | Enrichment Events Extracted |
|--------------|----------------------------|
| "How much does your community cost?" | `[{"event_type": "budget_inquiry", "event_data": {}, "confidence": 1.0}]` |
| "That's expensive. Do you take Medicaid?" | `[{"event_type": "budget_mentioned", "event_data": {"concern": "affordability"}, "confidence": 0.8}, {"event_type": "financing_inquiry", "event_data": {"type": "medicaid"}, "confidence": 1.0}]` |
| "My mom runs hot, she likes temperature very low" | `[{"event_type": "preference_stated", "event_data": {"category": "room_amenities", "detail": "individual AC control"}, "confidence": 0.9}]` |
| "How much for a 2 bedroom in assisted living?" | `[{"event_type": "room_type_interest", "event_data": {"type": "2_bedroom"}, "confidence": 1.0}, {"event_type": "care_need_expressed", "event_data": {"care_level": "assisted_living"}, "confidence": 0.9}]` |
| "Mom has Dementia, dad wants to stay with her" | `[{"event_type": "care_need_expressed", "event_data": {"condition": "dementia", "care_level": "memory_care"}, "confidence": 1.0}, {"event_type": "preference_stated", "event_data": {"category": "living_arrangement", "detail": "couples living together"}, "confidence": 1.0}]` |
| "Mom has a golden retriever" | `[{"event_type": "preference_stated", "event_data": {"category": "pets", "detail": "golden retriever", "size": "large"}, "confidence": 1.0}]` |
| "Can I get Kosher and low sodium meals?" | `[{"event_type": "preference_stated", "event_data": {"category": "dietary", "detail": ["kosher", "low_sodium"]}, "confidence": 1.0}]` |

---

## 6. Real-Time Understanding Summary

### 6.1 Feature Description

**Purpose**: Show users what the agent currently understands about their needs

**Benefits**:
- Transparency builds trust
- Catches misunderstandings early
- Demonstrates enrichment capability
- Unique differentiator

**Display**: Always-visible panel in chat UI (not collapsible, always shown)

### 6.2 Understanding Updater Logic

After each enrichment event extraction, update `current_understanding` field:

```python
def update_current_understanding(session, enrichment_events):
    """
    Update current_understanding based on new enrichment events
    """
    understanding = session.current_understanding or {}

    for event in enrichment_events:
        event_type = event['event_type']
        event_data = event['event_data']

        if event_type == 'budget_inquiry':
            understanding['budget_interest'] = "$2000+ pricing range"

        elif event_type == 'budget_mentioned':
            if 'range' in event_data:
                understanding['budget_interest'] = event_data['range']
            elif 'max' in event_data:
                understanding['budget_interest'] = f"Up to ${event_data['max']}/month"

        elif event_type == 'care_need_expressed':
            care_needs = understanding.get('care_needs', [])
            if 'condition' in event_data:
                care_needs.append(event_data['condition'].title())
            if 'care_level' in event_data:
                care_needs.append(event_data['care_level'].replace('_', ' ').title())
            understanding['care_needs'] = list(set(care_needs))  # dedupe

        elif event_type == 'timeline_shared':
            understanding['timeline'] = event_data.get('urgency', 'Exploring options').title()

        elif event_type == 'preference_stated':
            prefs = understanding.get('preferences', [])
            category = event_data.get('category', '')
            detail = event_data.get('detail', '')
            prefs.append(f"{category.replace('_', ' ').title()}: {detail}")
            understanding['preferences'] = prefs

        elif event_type == 'tour_requested':
            understanding['tour_interest'] = "High - wants to visit"

    session.current_understanding = understanding
    session.save()
```

### 6.3 UI Display Format

```jsx
// React component
<div className="understanding-panel">
  <h3>Current Understanding 📋</h3>

  {understanding.budget_interest && (
    <div className="understanding-item">
      <strong>Budget Interest:</strong> {understanding.budget_interest}
    </div>
  )}

  {understanding.care_needs && (
    <div className="understanding-item">
      <strong>Care Needs:</strong> {understanding.care_needs.join(', ')}
    </div>
  )}

  {understanding.timeline && (
    <div className="understanding-item">
      <strong>Timeline:</strong> {understanding.timeline}
    </div>
  )}

  {understanding.preferences && (
    <div className="understanding-item">
      <strong>Preferences:</strong>
      <ul>
        {understanding.preferences.map(pref => (
          <li key={pref}>{pref}</li>
        ))}
      </ul>
    </div>
  )}

  {understanding.tour_interest && (
    <div className="understanding-item">
      <strong>Tour Interest:</strong> {understanding.tour_interest}
    </div>
  )}
</div>
```

---

## 7. LangGraph Workflow

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

class ConversationState(TypedDict):
    session_id: str
    user_message: str
    conversation_history: List[dict]
    intent: str
    agent_response: str
    rag_context: List[dict]
    enrichment_events: List[dict]
    current_understanding: dict

# Initialize workflow
workflow = StateGraph(ConversationState)

# Add nodes
workflow.add_node("classify_intent", classify_intent_node)
workflow.add_node("pricing_agent", pricing_agent_node)
workflow.add_node("tour_scheduling_agent", tour_scheduling_agent_node)
workflow.add_node("amenities_agent", amenities_agent_node)
workflow.add_node("general_info_agent", general_info_agent_node)
workflow.add_node("extract_enrichment", extract_enrichment_node)
workflow.add_node("update_understanding", update_understanding_node)

# Entry point
workflow.set_entry_point("classify_intent")

# Conditional routing based on intent
def route_to_agent(state: ConversationState) -> str:
    intent_map = {
        "pricing": "pricing_agent",
        "tour_scheduling": "tour_scheduling_agent",
        "amenities": "amenities_agent",
        "general_info": "general_info_agent",
    }
    return intent_map.get(state["intent"], "general_info_agent")

workflow.add_conditional_edges(
    "classify_intent",
    route_to_agent,
    {
        "pricing_agent": "pricing_agent",
        "tour_scheduling_agent": "tour_scheduling_agent",
        "amenities_agent": "amenities_agent",
        "general_info_agent": "general_info_agent",
    }
)

# All agents flow through enrichment extraction
for agent in ["pricing_agent", "tour_scheduling_agent", "amenities_agent", "general_info_agent"]:
    workflow.add_edge(agent, "extract_enrichment")

# Enrichment flows to understanding updater
workflow.add_edge("extract_enrichment", "update_understanding")

# End workflow
workflow.add_edge("update_understanding", END)

# Compile
app = workflow.compile()
```

---

## 8. API Specifications

### 8.1 Chat Endpoint

**POST /api/chat**

```json
// Request
{
  "session_id": "uuid-or-null",  // null for new session
  "message": "How much does it cost?"
}

// Response
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Our community starts at $2000/month for Independent Living...",
  "agent_used": "pricing_agent",
  "current_understanding": {
    "budget_interest": "$2000+ pricing range"
  },
  "langfuse_trace_url": "https://cloud.langfuse.com/trace/abc123"
}
```

### 8.2 Get Current Understanding

**GET /api/session/{session_id}/understanding**

```json
// Response
{
  "budget_interest": "$3000-$4000/month",
  "care_needs": ["Assisted Living", "Memory care support"],
  "timeline": "Immediate",
  "preferences": ["Pet: golden retriever", "Dietary: Kosher, low sodium"],
  "tour_interest": "High - wants to visit"
}
```

### 8.3 Admin: List Prospects

**GET /api/admin/prospects**

```json
// Response
[
  {
    "prospect_id": "uuid",
    "first_name": "James",
    "last_name": "Smith",
    "email": "james@email.com",
    "phone": "555-1234",
    "tour_scheduled": true,
    "tour_datetime": "2025-03-10T14:00:00Z",
    "enrichment_count": 5,
    "created_at": "2025-03-04T10:30:00Z"
  }
]
```

### 8.4 Admin: Prospect Detail

**GET /api/admin/prospects/{prospect_id}**

```json
// Response
{
  "prospect": {
    "prospect_id": "uuid",
    "first_name": "James",
    "last_name": "Smith",
    "email": "james@email.com",
    "phone": "555-1234",
    "tour_scheduled": true,
    "tour_datetime": "2025-03-10T14:00:00Z"
  },
  "enrichment_events": [
    {
      "event_id": "uuid",
      "event_type": "budget_inquiry",
      "event_data": {},
      "extracted_by_agent": "pricing_agent",
      "source_message": "How much does it cost?",
      "created_at": "2025-03-04T10:30:00Z"
    },
    {
      "event_id": "uuid",
      "event_type": "care_need_expressed",
      "event_data": {
        "condition": "dementia",
        "care_level": "assisted_living"
      },
      "extracted_by_agent": "general_info_agent",
      "source_message": "My mom has dementia",
      "created_at": "2025-03-04T10:33:00Z"
    }
  ],
  "conversation_history": [
    {
      "role": "user",
      "content": "How much does it cost?",
      "timestamp": "2025-03-04T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Our community starts at $2000/month...",
      "agent": "pricing_agent",
      "timestamp": "2025-03-04T10:30:02Z"
    }
  ]
}
```

### 8.5 Test Agent (Development/Demo)

**POST /api/test/agent/{agent_name}**

```json
// Request
{
  "user_message": "How much does it cost?",
  "conversation_context": {
    "session_id": "test",
    "conversation_history": []
  }
}

// Response
{
  "agent_response": "Our community starts at $2000/month for Independent Living...",
  "rag_context_used": [
    {
      "content": "Independent Living starts from $2000 a month...",
      "similarity_score": 0.92
    }
  ],
  "enrichment_events_extracted": [
    {
      "event_type": "budget_inquiry",
      "event_data": {},
      "confidence": 1.0
    }
  ],
  "langfuse_trace_url": "https://cloud.langfuse.com/trace/test123"
}
```

---

## 9. Deployment Architecture

### Docker Compose

```yaml
version: '3.8'

services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: acme_sales_agent
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/acme_sales_agent
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
      - LANGFUSE_HOST=https://cloud.langfuse.com
    ports:
      - "8000:8000"
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000

  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000

  admin:
    build: ./admin
    depends_on:
      - backend
    ports:
      - "3001:3000"
    environment:
      - VITE_API_URL=http://localhost:8000

volumes:
  pgdata:
```

### Railway Deployment

- **PostgreSQL**: Railway addon with pgvector extension
- **Backend**: Django service (gunicorn)
- **Frontend**: React chat UI (static build)
- **Admin**: React admin dashboard (static build)

---

## 10. Privacy & Security Notice

**This prototype does NOT implement:**
- Data encryption at rest or in transit
- PII anonymization
- HIPAA compliance for health information
- Access controls / authentication
- Audit logging for data access
- Data retention policies
- User consent management

**Production requirements would include:**
- End-to-end encryption
- Role-based access control (RBAC)
- HIPAA compliance measures
- SOC 2 Type II compliance
- Data anonymization for analytics
- Regular security audits

---

## 11. Technology Stack

**Backend:**
- Python 3.11+
- Django 5.0
- PostgreSQL 16 with pgvector extension
- LangChain
- LangGraph
- LangFuse SDK
- OpenAI SDK (GPT-4, text-embedding-3-small)
- uv for package management

**Frontend (Chat UI):**
- React 18
- Vite
- Tailwind CSS
- WebSocket or REST polling for real-time updates

**Admin Dashboard:**
- React 18
- Vite
- Tailwind CSS
- Separate app from chat UI

**Infrastructure:**
- Docker & Docker Compose
- Railway (deployment)
- LangFuse Cloud (observability)

---

## 12. Success Metrics

### Technical Metrics
- **Agent response latency**: P95 < 2 seconds
- **RAG retrieval accuracy**: >90% relevant results in top-3
- **Intent classification accuracy**: >90% (manual review sample)
- **System uptime**: >99% during demo

### Business Value Metrics
- **Enrichment capture rate**: >80% of relevant user statements captured as events
- **Understanding accuracy**: Real-time summary matches actual user intent (manual review)
- **Admin usability**: Community manager can understand prospect context in <30 seconds
- **Tour conversion**: (Future) Prospects who see understanding summary convert at higher rate

### Demo Goals
- ✅ Show multi-agent architecture working
- ✅ Demonstrate RAG-based factual responses
- ✅ Show enrichment event capture
- ✅ Display real-time understanding transparency
- ✅ Show admin dashboard with context for tours
- ✅ Demonstrate LangFuse observability
- ✅ Test individual agents in isolation
