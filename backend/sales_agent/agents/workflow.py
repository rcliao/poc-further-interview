"""
LangGraph workflow for multi-agent sales conversation system
"""
import os
from typing import TypedDict, List, Dict, Annotated, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from sales_agent.rag import retriever
# TODO: Re-enable LangFuse observability with correct API
# from langfuse import Langfuse
# from langfuse.decorators import observe, langfuse_context


# Pydantic models for structured output
class EnrichmentEventData(BaseModel):
    """Data extracted from an enrichment event"""
    condition: Optional[str] = None
    care_level: Optional[str] = None
    range: Optional[str] = None
    max: Optional[int] = None
    urgency: Optional[str] = None
    category: Optional[str] = None
    detail: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    financing_type: Optional[str] = None  # e.g., "Medicaid", "Medicare", "VA benefits", "insurance"
    pet_type: Optional[str] = None  # e.g., "golden retriever", "cat", "small dog"
    car_interest: Optional[bool] = None  # True if asking about bringing car/parking


class EnrichmentEvent(BaseModel):
    """Single enrichment event extracted from conversation"""
    event_type: str = Field(description="Type of enrichment event (e.g., budget_inquiry, care_need_expressed)")
    event_data: EnrichmentEventData = Field(default_factory=EnrichmentEventData, description="Additional structured data for this event")
    source_message: str = Field(description="The user message that triggered this event")
    confidence: float = Field(default=1.0, description="Confidence score for this extraction (0.0-1.0)")


class EnrichmentEventList(BaseModel):
    """List of enrichment events"""
    events: List[EnrichmentEvent] = Field(default_factory=list, description="List of extracted enrichment events")


# Conversation State Definition
class ConversationState(TypedDict):
    """
    State maintained throughout the conversation workflow
    """
    session_id: str
    user_message: str
    conversation_history: List[Dict[str, str]]
    intent: str
    agent_response: str
    rag_context: List[Dict]
    enrichment_events: List[Dict]
    current_understanding: Dict[str, any]


# TODO: Re-enable LangFuse initialization
# langfuse = Langfuse(
#     secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
#     public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
#     host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
# )


# Initialize LLM
def get_llm():
    """Get OpenAI LLM instance"""
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )


# Agent Node: Intent Classifier
def classify_intent_node(state: ConversationState) -> ConversationState:
    """
    Classify user intent to route to appropriate agent
    """
    llm = get_llm()
    user_message = state["user_message"]
    history = state.get("conversation_history", [])[-30:]  # Last 30 messages for comprehensive context

    # Rule-based check: If last assistant message was asking for contact info during tour scheduling, keep the intent
    if history:
        last_assistant_msg = None
        last_intent = None
        for msg in reversed(history):
            if msg.get("role") == "assistant":
                last_assistant_msg = msg.get("content", "").lower()
                last_intent = msg.get("intent")
                break

        # If we were in tour_scheduling and asking for contact info, stay in tour_scheduling
        if last_intent == "tour_scheduling" and last_assistant_msg:
            contact_keywords = ["name", "email", "phone", "contact", "reach you", "full name"]
            if any(keyword in last_assistant_msg for keyword in contact_keywords):
                # User is likely providing contact info, keep tour_scheduling intent
                state["intent"] = "tour_scheduling"
                return state

    prompt = f"""You are an intent classifier for a senior living sales assistant.

Classify the user's intent into ONE category:
- pricing: Cost, fees, monthly rates, what's included in price
- tour_scheduling: Schedule tour, visit, see the community, OR providing contact info (name/email/phone) during tour booking
- amenities: Facilities, services, activities, dining, what's available
- financing: Medicaid, insurance, payment options, financial assistance
- general_info: Everything else (contact info, policies, room types, care types, etc.)

IMPORTANT:
- If the assistant just asked for name, email, or phone number, and the user is responding with that information, classify as "tour_scheduling"
- Look at the recent conversation to detect ongoing information collection flows
- A phone number, email, or name by itself during tour scheduling should be classified as "tour_scheduling"

User message: {user_message}
Recent context: {history}

Return ONLY the category name, nothing else."""

    response = llm.invoke(prompt)
    intent = response.content.strip().lower()

    state["intent"] = intent
    return state


# Agent Node: Pricing Agent
def pricing_agent_node(state: ConversationState) -> ConversationState:
    """
    Handle pricing inquiries
    """
    llm = get_llm()
    user_message = state["user_message"]
    history = state.get("conversation_history", [])

    # Retrieve pricing knowledge
    rag_results = retriever.search(user_message, category_filter=["pricing"], top_k=3)

    state["rag_context"] = rag_results

    # Format RAG context
    knowledge_context = "\n".join([f"- {item['content']}" for item in rag_results])

    prompt = f"""You are Sophie, a sales specialist at ACME Senior Living.

Answer the user's pricing question using ONLY the facts provided below.

PRICING FACTS (from Step 5):
- Community starts at $2,000/month
- Assisted Living starts from $3,000/month
- Independent Living starts from $2,000/month
- Entrance fee: $3,500
- Included in monthly cost: Basic Cable, Internet/WiFi, Linen Service, Breakfast, Lunch, Dinner, Housekeeping
- You do NOT have information on pricing per room type or size

Additional Knowledge Base:
{knowledge_context}

Guidelines:
- Be warm and conversational
- Provide the specific pricing information above when asked about costs
- If asked about specific room pricing, say: "I don't have pricing per room type, but I can share our general rates. Would you like to hear those?"
- After answering, ALWAYS suggest scheduling a tour
- Keep response to 2-3 sentences maximum

Conversation history: {history[-2:] if history else []}
User's question: {user_message}

Your response:"""

    response = llm.invoke(prompt)
    state["agent_response"] = response.content

    return state


# Agent Node: Tour Scheduling Agent
def tour_scheduling_agent_node(state: ConversationState) -> ConversationState:
    """
    Handle tour scheduling requests and collect contact information
    """
    llm = get_llm()
    user_message = state["user_message"]
    history = state.get("conversation_history", [])

    # Retrieve tour availability
    rag_results = retriever.search("tour availability hours", category_filter=["tour"], top_k=1)
    state["rag_context"] = rag_results
    knowledge_context = "\n".join([f"- {item['content']}" for item in rag_results])

    # Check conversation history to see if we're collecting contact info
    conversation_context = "\n".join([
        f"{msg.get('role', 'user')}: {msg.get('content', '')}"
        for msg in history[-30:] if msg.get('content')
    ])

    # Get current date and time
    from datetime import datetime
    current_datetime = datetime.now().strftime("%A, %B %d, %Y, %I:%M %p")

    prompt = f"""You are Sophie, a tour scheduling specialist at ACME Senior Living.

Tour Availability:
{knowledge_context}
Tours are available Monday-Friday from 9:00 AM to 6:00 PM. We are closed on weekends.

Current date and time: {current_datetime}

Recent conversation:
{conversation_context}

User's latest message: {user_message}

YOUR TASK: Help schedule a tour by collecting: date/time, name, email, and phone.

INSTRUCTIONS:
1. If user requests a tour, suggest a specific Monday-Friday time between 9 AM-6 PM
2. If they request weekend/outside hours, politely offer Monday-Friday alternative
3. Once they confirm a time works, collect contact info in order: name → email → phone

HOW TO COLLECT CONTACT INFO:
- Look at your last message to see what you just asked for
- If you asked "Could you provide your full name?" and got a name → ask for EMAIL next
- If you asked for email and got an email address → ask for PHONE next
- If you asked for phone and got a phone number → confirm the tour is scheduled

IMPORTANT RULES:
- Only ask for ONE piece of information per message
- NEVER repeat a question you just asked
- Progress forward: name → email → phone
- Keep responses short (2-3 sentences)

Your response:"""

    response = llm.invoke(prompt)
    state["agent_response"] = response.content

    return state


# Agent Node: Amenities Agent
def amenities_agent_node(state: ConversationState) -> ConversationState:
    """
    Handle questions about community features
    """
    llm = get_llm()
    user_message = state["user_message"]

    # Retrieve amenities knowledge (including policies like pets, cars, smoking)
    rag_results = retriever.search(user_message, category_filter=["amenities", "services", "activities", "dietary", "room_amenities", "policies"], top_k=3)

    state["rag_context"] = rag_results

    knowledge_context = "\n".join([f"- {item['content']}" for item in rag_results])

    prompt = f"""You are Sophie, a specialist in community amenities and policies at ACME Senior Living.

Answer the user's question using ONLY the facts below.

Available Information:
{knowledge_context}

Guidelines:
- Answer questions about amenities, services, activities, AND policies (pets, cars, parking, smoking, visiting, etc.)
- List 2-3 specific items from the category they asked about
- Be clear and direct when we have the information
- If something is NOT in the knowledge base, say: "I don't have specific information about that, but I can connect you with our team to find out."
- Be enthusiastic but factual
- Keep response to 2-3 sentences

User's question: {user_message}

Your response:"""

    response = llm.invoke(prompt)
    state["agent_response"] = response.content

    return state


# Agent Node: Financing Agent
def financing_agent_node(state: ConversationState) -> ConversationState:
    """
    Handle questions about payment options, Medicaid, insurance, etc.
    """
    llm = get_llm()
    user_message = state["user_message"]

    # Retrieve financing knowledge
    rag_results = retriever.search(user_message, category_filter=["financing"], top_k=3)

    state["rag_context"] = rag_results

    knowledge_context = "\n".join([f"- {item['content']}" for item in rag_results])

    prompt = f"""You are Sophie, a financial specialist at ACME Senior Living.

Answer the user's question using ONLY the facts below.

Available Information:
{knowledge_context}

Guidelines:
- If asked about Medicaid: YES, we participate in Medicaid programs
- If asked about insurance: We do NOT accept long term care insurance
- If asked about veterans: Veterans may be eligible for Veterans benefits
- If asked about payment help: We offer bridge loans for homeowners and participate in HUD programs
- Be clear and direct about what we accept and don't accept
- Keep response to 2-3 sentences

User's question: {user_message}

Your response:"""

    response = llm.invoke(prompt)
    state["agent_response"] = response.content

    return state


# Agent Node: General Info Agent
def general_info_agent_node(state: ConversationState) -> ConversationState:
    """
    Fallback agent for general questions
    """
    llm = get_llm()
    user_message = state["user_message"]

    # Broad search across all categories
    rag_results = retriever.search(user_message, top_k=5)

    state["rag_context"] = rag_results

    knowledge_context = "\n".join([f"- {item['content']}" for item in rag_results])

    prompt = f"""You are Sophie, a sales specialist at ACME Senior Living.

Answer the user's question using ONLY the facts below.

Available Information:
{knowledge_context}

Guidelines:
- Use the provided facts to answer
- If the knowledge base doesn't contain the answer, say: "I don't have specific information about that. Would you like me to connect you with our team?"
- Be warm and helpful
- Keep response to 2-3 sentences

User's question: {user_message}

Your response:"""

    response = llm.invoke(prompt)
    state["agent_response"] = response.content

    return state


# Agent Node: Enrichment Extractor
def extract_enrichment_node(state: ConversationState) -> ConversationState:
    """
    Extract enrichment events from conversation using LLM with structured output
    """
    # Use structured output for reliable JSON extraction
    llm = get_llm()
    structured_llm = llm.with_structured_output(EnrichmentEventList)

    user_message = state["user_message"]
    agent_response = state["agent_response"]
    agent_name = state.get("intent", "unknown") + "_agent"

    prompt = f"""Analyze the user's message and identify any enrichment events.

User message: "{user_message}"
Agent response: "{agent_response}"
Agent type: "{agent_name}"

Event types to extract:
- budget_inquiry: User asked about pricing
- budget_mentioned: User stated specific budget (extract amount/range in event_data)
- care_need_expressed: User mentioned care needs, conditions, or assistance required
- timeline_shared: User indicated urgency or move timeline
- preference_stated: User mentioned preferences - IMPORTANT: Extract specific details:
  * Pets: If asking about pets or mentioning bringing a pet, extract pet type and any details (e.g., "golden retriever")
  * Cars/Parking: If asking about bringing a car or parking
  * Dietary needs, couples living together, smoking, etc.
- tour_requested: User expressed interest in visiting
- tour_scheduled: Tour confirmed with date/time (extract date and time in event_data)
- contact_shared: User provided name, email, or phone number (extract to event_data)
- financing_inquiry: User asked about payment/financial assistance (Medicaid, Medicare, insurance, VA benefits, bridge loans, etc.) - ALWAYS extract this when user mentions any payment help
- room_type_interest: User asked about specific room types

For each event, extract:
- event_type: One of the types above
- event_data: Relevant structured data, including:
  - For financing_inquiry: {{"financing_type": "Medicaid"}} or "Medicare", "insurance", "VA benefits", etc.
  - For care needs: {{"condition": "dementia"}}
  - For budget: {{"max": 4000}}
  - For contact: {{"name": "Eric"}}, {{"email": "eric@example.com"}}, {{"phone": "555-1234"}}
  - For pets preference: {{"category": "pets", "detail": "golden retriever", "pet_type": "golden retriever"}}
  - For car preference: {{"category": "parking", "detail": "wants to bring car", "car_interest": true}}
- source_message: The exact user message
- confidence: How confident you are (0.0-1.0)

Return all identified events."""

    try:
        result = structured_llm.invoke(prompt)
        # Convert Pydantic models to dicts for storage
        events = [event.model_dump() for event in result.events]
        state["enrichment_events"] = events
    except Exception as e:
        # Log error but continue gracefully
        import sys
        print(f"Error extracting enrichment events: {e}", file=sys.stderr)
        state["enrichment_events"] = []

    return state


# Agent Node: Understanding Updater
def update_understanding_node(state: ConversationState) -> ConversationState:
    """
    Update current understanding based on enrichment events
    """
    understanding = state.get("current_understanding", {})
    events = state.get("enrichment_events", [])

    for event in events:
        event_type = event.get("event_type")
        event_data = event.get("event_data", {})

        if event_type == "budget_inquiry":
            # Just track that they asked about pricing, don't assume a budget
            understanding["budget_interest"] = "Inquired about pricing"

        elif event_type == "budget_mentioned":
            if event_data.get("range"):
                understanding["budget_interest"] = event_data["range"]
            elif event_data.get("max"):
                understanding["budget_interest"] = f"Up to ${event_data['max']}/month"

        elif event_type == "care_need_expressed":
            care_needs = understanding.get("care_needs", [])
            if event_data.get("condition"):
                care_needs.append(event_data["condition"].title())
            if event_data.get("care_level"):
                care_needs.append(event_data["care_level"].replace("_", " ").title())
            understanding["care_needs"] = list(set(care_needs))  # dedupe

        elif event_type == "timeline_shared":
            urgency = event_data.get("urgency") or "Exploring options"
            understanding["timeline"] = urgency.title()

        elif event_type == "preference_stated":
            prefs = understanding.get("preferences", [])
            category = event_data.get("category") or ""
            detail = event_data.get("detail") or ""
            if category:
                prefs.append(f"{category.replace('_', ' ').title()}: {detail}")
                understanding["preferences"] = prefs

        elif event_type == "tour_requested":
            understanding["tour_interest"] = "High - wants to visit"

        elif event_type == "tour_scheduled":
            tour_date = event_data.get("date")
            tour_time = event_data.get("time")
            if tour_date and tour_time:
                understanding["tour_scheduled"] = f"{tour_date} at {tour_time}"
            elif tour_date or tour_time:
                understanding["tour_scheduled"] = tour_date or tour_time

        elif event_type == "contact_shared":
            # Collect contact information
            if event_data.get("name"):
                understanding["name"] = event_data["name"]
            if event_data.get("email"):
                understanding["email"] = event_data["email"]
            if event_data.get("phone"):
                understanding["phone"] = event_data["phone"]

        elif event_type == "financing_inquiry":
            # Track what financing options they asked about
            financing_interests = understanding.get("financing_interests", [])
            financing_type = event_data.get("financing_type", "Payment options")
            if financing_type not in financing_interests:
                financing_interests.append(financing_type)
            understanding["financing_interests"] = financing_interests

    state["current_understanding"] = understanding

    return state


# Routing Logic
def route_to_agent(state: ConversationState) -> str:
    """
    Route to appropriate agent based on intent
    """
    intent = state.get("intent", "general_info")

    intent_map = {
        "pricing": "pricing_agent",
        "tour_scheduling": "tour_scheduling_agent",
        "amenities": "amenities_agent",
        "financing": "financing_agent",
        "general_info": "general_info_agent",
    }

    return intent_map.get(intent, "general_info_agent")


# Build Workflow
def create_workflow() -> StateGraph:
    """
    Create and compile the LangGraph workflow
    """
    workflow = StateGraph(ConversationState)

    # Add nodes
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("pricing_agent", pricing_agent_node)
    workflow.add_node("tour_scheduling_agent", tour_scheduling_agent_node)
    workflow.add_node("amenities_agent", amenities_agent_node)
    workflow.add_node("financing_agent", financing_agent_node)
    workflow.add_node("general_info_agent", general_info_agent_node)
    workflow.add_node("extract_enrichment", extract_enrichment_node)
    workflow.add_node("update_understanding", update_understanding_node)

    # Entry point
    workflow.set_entry_point("classify_intent")

    # Conditional routing from intent classifier
    workflow.add_conditional_edges(
        "classify_intent",
        route_to_agent,
        {
            "pricing_agent": "pricing_agent",
            "tour_scheduling_agent": "tour_scheduling_agent",
            "amenities_agent": "amenities_agent",
            "financing_agent": "financing_agent",
            "general_info_agent": "general_info_agent",
        }
    )

    # All agents flow to enrichment extraction
    for agent in ["pricing_agent", "tour_scheduling_agent", "amenities_agent", "financing_agent", "general_info_agent"]:
        workflow.add_edge(agent, "extract_enrichment")

    # Enrichment flows to understanding updater
    workflow.add_edge("extract_enrichment", "update_understanding")

    # End workflow
    workflow.add_edge("update_understanding", END)

    # Compile
    return workflow.compile()


# Global compiled workflow
compiled_workflow = create_workflow()
