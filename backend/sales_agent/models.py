import uuid
from django.db import models
from pgvector.django import VectorField


class Prospect(models.Model):
    """
    Represents a person inquiring about ACME Senior Living
    Minimal model - enrichment stored as events, not flattened attributes
    """
    prospect_id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # Contact Info (collected during tour scheduling)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    # Tour Details
    tour_scheduled = models.BooleanField(default=False)
    tour_datetime = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tour_scheduled']),
        ]

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return f"Prospect {self.prospect_id}"


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
        blank=True,
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

    def __str__(self):
        return f"Session {self.session_id} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"


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

    def __str__(self):
        return f"{self.event_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


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

    def __str__(self):
        return f"{self.category}: {self.content[:50]}..."
