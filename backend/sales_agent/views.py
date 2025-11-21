"""
API views for sales agent conversation and admin endpoints
"""
import uuid
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import re

from sales_agent.models import Prospect, ConversationSession, EnrichmentEvent
from sales_agent.agents.workflow import compiled_workflow


def parse_tour_datetime(date_str, time_str):
    """
    Parse relative date and time strings into a timezone-aware datetime object.
    Examples: "Tuesday", "next Monday", "2 PM", "10:30 AM"
    """
    try:
        from datetime import datetime as dt
        import pytz

        # Get the timezone from Django settings (default to America/Los_Angeles)
        tz = pytz.timezone('America/Los_Angeles')
        now = timezone.now().astimezone(tz)

        # Parse time
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)', time_str or "")
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            period = time_match.group(3).upper()

            if period == "PM" and hour != 12:
                hour += 12
            elif period == "AM" and hour == 12:
                hour = 0
        else:
            hour, minute = 14, 0  # Default to 2 PM

        # Parse date - handle day names
        days_of_week = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }

        date_lower = (date_str or "").lower()
        target_day = None

        for day_name, day_num in days_of_week.items():
            if day_name in date_lower:
                target_day = day_num
                break

        if target_day is not None:
            current_day = now.weekday()
            days_ahead = target_day - current_day

            # If "next" is in the string, add 7 days
            if "next" in date_lower:
                days_ahead += 7
            elif days_ahead <= 0:
                days_ahead += 7  # Move to next week if day has passed

            # Create a naive datetime for the target date/time
            target_date = now.date() + timedelta(days=days_ahead)
            naive_datetime = dt.combine(target_date, dt.min.time().replace(hour=hour, minute=minute))

            # Make it timezone-aware in the local timezone
            tour_datetime = tz.localize(naive_datetime)
            return tour_datetime

        return None
    except Exception as e:
        print(f"Error parsing tour datetime: {e}")
        return None


@api_view(['POST'])
def chat(request):
    """
    POST /api/chat

    Handle user messages and return agent responses

    Request body:
    {
        "session_id": "optional-session-uuid",
        "message": "User's message",
        "prospect_id": "optional-prospect-uuid"
    }

    Response:
    {
        "session_id": "uuid",
        "prospect_id": "uuid",
        "response": "Agent's response",
        "intent": "pricing|tour_scheduling|amenities|financing|general_info",
        "current_understanding": {...}
    }
    """
    try:
        # Extract request data
        user_message = request.data.get('message')
        session_id = request.data.get('session_id')
        prospect_id = request.data.get('prospect_id')

        if not user_message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create prospect
        if prospect_id:
            try:
                prospect = Prospect.objects.get(prospect_id=prospect_id)
            except Prospect.DoesNotExist:
                prospect = Prospect.objects.create()
        else:
            prospect = Prospect.objects.create()

        # Get or create conversation session
        if session_id:
            try:
                session = ConversationSession.objects.get(
                    session_id=session_id,
                    prospect=prospect
                )
            except ConversationSession.DoesNotExist:
                session = ConversationSession.objects.create(
                    prospect=prospect,
                    conversation_history=[],
                    current_understanding={}
                )
        else:
            session = ConversationSession.objects.create(
                prospect=prospect,
                conversation_history=[],
                current_understanding={}
            )

        # Prepare workflow state
        state = {
            "session_id": str(session.session_id),
            "user_message": user_message,
            "conversation_history": session.conversation_history,
            "intent": "",
            "agent_response": "",
            "rag_context": [],
            "enrichment_events": [],
            "current_understanding": session.current_understanding
        }

        # Execute workflow
        result = compiled_workflow.invoke(state)

        # Update conversation history
        session.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": timezone.now().isoformat()
        })
        session.conversation_history.append({
            "role": "assistant",
            "content": result["agent_response"],
            "timestamp": timezone.now().isoformat(),
            "intent": result["intent"]
        })

        # Update current understanding
        session.current_understanding = result["current_understanding"]
        session.save()

        # Save enrichment events to database
        for event in result.get("enrichment_events", []):
            EnrichmentEvent.objects.create(
                session=session,
                event_type=event.get("event_type"),
                event_data=event.get("event_data", {}),
                extracted_by_agent=result["intent"] + "_agent",
                source_message=event.get("source_message", user_message),
                confidence=event.get("confidence", 1.0)
            )

        # Update prospect with contact information if collected
        understanding = result["current_understanding"]
        prospect_updated = False
        if understanding.get("name") and not prospect.first_name:
            # Split name into first and last
            name_parts = understanding["name"].strip().split(maxsplit=1)
            prospect.first_name = name_parts[0]
            if len(name_parts) > 1:
                prospect.last_name = name_parts[1]
            prospect_updated = True
        if understanding.get("email") and not prospect.email:
            prospect.email = understanding["email"]
            prospect_updated = True
        if understanding.get("phone") and not prospect.phone:
            prospect.phone = understanding["phone"]
            prospect_updated = True
        if understanding.get("tour_scheduled"):
            # Parse and store the tour datetime
            prospect.tour_scheduled = True

            # Try to get date and time from enrichment events
            tour_date = None
            tour_time = None
            for event in result.get("enrichment_events", []):
                if event.get("event_type") == "tour_scheduled":
                    event_data = event.get("event_data", {})
                    tour_date = event_data.get("date")
                    tour_time = event_data.get("time")
                    break

            # Parse and store the datetime
            if tour_date or tour_time:
                parsed_datetime = parse_tour_datetime(tour_date, tour_time)
                if parsed_datetime:
                    prospect.tour_datetime = parsed_datetime

            prospect_updated = True
        if prospect_updated:
            prospect.save()

        # Return response
        return Response({
            "session_id": str(session.session_id),
            "prospect_id": str(prospect.prospect_id),
            "response": result["agent_response"],
            "intent": result["intent"],
            "current_understanding": result["current_understanding"]
        })

    except Exception as e:
        return Response(
            {"error": f"Internal server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_prospects(request):
    """
    GET /api/admin/prospects

    List all prospects with their conversation summaries

    Response:
    {
        "prospects": [
            {
                "prospect_id": "uuid",
                "first_name": "string",
                "last_name": "string",
                "email": "string",
                "phone": "string",
                "tour_scheduled": boolean,
                "tour_datetime": "iso-datetime",
                "total_sessions": number,
                "last_interaction": "iso-datetime",
                "current_understanding": {...}
            }
        ]
    }
    """
    try:
        prospects = Prospect.objects.all().order_by('-created_at')

        prospects_data = []
        for prospect in prospects:
            # Get latest session for this prospect
            latest_session = ConversationSession.objects.filter(
                prospect=prospect
            ).order_by('-updated_at').first()

            prospects_data.append({
                "prospect_id": str(prospect.prospect_id),
                "first_name": prospect.first_name,
                "last_name": prospect.last_name,
                "email": prospect.email,
                "phone": prospect.phone,
                "tour_scheduled": prospect.tour_scheduled,
                "tour_datetime": prospect.tour_datetime.isoformat() if prospect.tour_datetime else None,
                "total_sessions": ConversationSession.objects.filter(prospect=prospect).count(),
                "last_interaction": latest_session.updated_at.isoformat() if latest_session else None,
                "current_understanding": latest_session.current_understanding if latest_session else {}
            })

        return Response({"prospects": prospects_data})

    except Exception as e:
        return Response(
            {"error": f"Internal server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def prospect_detail(request, prospect_id):
    """
    GET /api/admin/prospects/{prospect_id}

    Get detailed information for a specific prospect

    Response:
    {
        "prospect": {
            "prospect_id": "uuid",
            "first_name": "string",
            "last_name": "string",
            "email": "string",
            "phone": "string",
            "tour_scheduled": boolean,
            "tour_datetime": "iso-datetime"
        },
        "sessions": [
            {
                "session_id": "uuid",
                "conversation_history": [...],
                "current_understanding": {...},
                "created_at": "iso-datetime",
                "last_interaction": "iso-datetime"
            }
        ],
        "enrichment_events": [
            {
                "event_type": "string",
                "event_data": {...},
                "extracted_by_agent": "string",
                "source_message": "string",
                "confidence": number,
                "created_at": "iso-datetime"
            }
        ]
    }
    """
    try:
        prospect = Prospect.objects.get(prospect_id=prospect_id)

        # Get all sessions for this prospect
        sessions = ConversationSession.objects.filter(
            prospect=prospect
        ).order_by('-updated_at')

        sessions_data = []
        for session in sessions:
            sessions_data.append({
                "session_id": str(session.session_id),
                "conversation_history": session.conversation_history,
                "current_understanding": session.current_understanding,
                "created_at": session.started_at.isoformat(),
                "last_interaction": session.updated_at.isoformat()
            })

        # Get all enrichment events across all sessions
        events = EnrichmentEvent.objects.filter(
            session__prospect=prospect
        ).order_by('-created_at')

        events_data = []
        for event in events:
            events_data.append({
                "event_type": event.event_type,
                "event_data": event.event_data,
                "extracted_by_agent": event.extracted_by_agent,
                "source_message": event.source_message,
                "confidence": event.confidence,
                "created_at": event.created_at.isoformat()
            })

        return Response({
            "prospect": {
                "prospect_id": str(prospect.prospect_id),
                "first_name": prospect.first_name,
                "last_name": prospect.last_name,
                "email": prospect.email,
                "phone": prospect.phone,
                "tour_scheduled": prospect.tour_scheduled,
                "tour_datetime": prospect.tour_datetime.isoformat() if prospect.tour_datetime else None
            },
            "sessions": sessions_data,
            "enrichment_events": events_data
        })

    except Prospect.DoesNotExist:
        return Response(
            {"error": "Prospect not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Internal server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def test_agent(request, agent_name):
    """
    POST /api/test/agent/{agent_name}

    Test a specific agent in isolation

    Request body:
    {
        "message": "User's test message"
    }

    Response:
    {
        "agent": "agent_name",
        "input": "message",
        "output": "agent response",
        "rag_context": [...],
        "metadata": {...}
    }
    """
    try:
        user_message = request.data.get('message')

        if not user_message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Map agent names to workflow nodes
        agent_map = {
            "intent": "classify_intent",
            "pricing": "pricing_agent",
            "tour": "tour_scheduling_agent",
            "amenities": "amenities_agent",
            "financing": "financing_agent",
            "general": "general_info_agent"
        }

        if agent_name not in agent_map:
            return Response(
                {"error": f"Invalid agent name. Available: {', '.join(agent_map.keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create minimal state for testing
        state = {
            "session_id": str(uuid.uuid4()),
            "user_message": user_message,
            "conversation_history": [],
            "intent": agent_name if agent_name != "intent" else "",
            "agent_response": "",
            "rag_context": [],
            "enrichment_events": [],
            "current_understanding": {}
        }

        # Import and call the specific agent function
        from sales_agent.agents.workflow import (
            classify_intent_node,
            pricing_agent_node,
            tour_scheduling_agent_node,
            amenities_agent_node,
            financing_agent_node,
            general_info_agent_node
        )

        agent_functions = {
            "intent": classify_intent_node,
            "pricing": pricing_agent_node,
            "tour": tour_scheduling_agent_node,
            "amenities": amenities_agent_node,
            "financing": financing_agent_node,
            "general": general_info_agent_node
        }

        # Execute the specific agent
        result = agent_functions[agent_name](state)

        return Response({
            "agent": agent_name,
            "input": user_message,
            "output": result.get("agent_response", result.get("intent", "")),
            "rag_context": result.get("rag_context", []),
            "metadata": {
                "intent": result.get("intent"),
                "enrichment_events": result.get("enrichment_events", [])
            }
        })

    except Exception as e:
        return Response(
            {"error": f"Internal server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
