from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.nlp.intent_recognizer import IntentRecognizer
from src.analysis.query_builder import QueryBuilder
from src.api.response_generator import ResponseGenerator
from src.api.conversation import ConversationManager

router = APIRouter()

# Initialize components
intent_recognizer = IntentRecognizer()
response_generator = ResponseGenerator()
conversation_manager = ConversationManager()

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    query: str
    intent: str
    explanation: str
    insights: list
    confidence_score: float
    raw_data: Dict[str, Any]
    session_id: Optional[str] = None

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Process natural language query with conversation context support for follow-ups.
    
    Pass session_id in context to maintain conversation continuity:
    Example: {"query": "...", "context": {"session_id": "..."}}
    """
    try:
        # Extract session context
        session_id = None
        if request.context and isinstance(request.context, dict):
            session_id = request.context.get("session_id")

        # Step 1: Recognize intent and extract entities
        intent_result = intent_recognizer.recognize_intent(request.query)

        # Step 2: Merge with conversation context for follow-ups
        if session_id:
            last_entities = conversation_manager.get_session(session_id).get("last_entities", {}) if conversation_manager.get_session(session_id) else {}
            last_intent = conversation_manager.get_session(session_id).get("last_intent") if conversation_manager.get_session(session_id) else None
            
            # Merge previous entities to handle follow-up references
            intent_result.entities = conversation_manager.merge_entities(
                session_id, 
                intent_result.entities
            )
            
            # Smart intent preservation: if follow-up query is just adding filters/metrics
            # but not changing the core analysis type, preserve the previous intent
            current_intent = intent_result.type
            is_just_filter = (intent_result.type == 'descriptive' and 
                            last_intent in ['comparative', 'risk_analysis', 'user_segmentation'])
            is_metric_change = (intent_result.type == 'comparative' and last_intent == 'comparative' and
                               'metric' in intent_result.entities)
            is_intent_mismatch = (intent_result.type != last_intent and 
                                 last_intent in ['risk_analysis', 'user_segmentation'])
            
            if is_just_filter or is_metric_change or is_intent_mismatch:
                intent_result.type = last_intent
            
            # If merged entities have comparison_dimension but intent is descriptive,
            # upgrade to comparative (follow-up that adds filter but maintains grouping)
            if intent_result.type == 'descriptive' and intent_result.entities.get('comparison_dimension'):
                intent_result.type = 'comparative'
        
        # Step 3: Build and execute query
        query_builder = QueryBuilder(db)
        analysis_result = query_builder.execute_query(
            intent_result.type,
            intent_result.entities,
            request.query  # Pass original query for pattern detection
        )
        
        # Step 4: Get conversation context for LLM
        conversation_context = None
        resolved_entities = intent_result.entities
        
        if session_id:
            conversation_context = conversation_manager.get_conversation_context(session_id)
            resolved_entities = conversation_manager.get_resolved_entities(session_id)
            # Merge current entities with resolved ones
            resolved_entities.update(intent_result.entities)
        
        # Step 5: Generate context-aware response
        response = response_generator.generate_response(
            request.query,
            analysis_result,
            intent_result.type,
            conversation_context=conversation_context,
            resolved_entities=resolved_entities
        )

        # Step 6: Create or update session
        if not session_id:
            session_id = conversation_manager.create_session()

        # Update session with the new turn (include AI response)
        conversation_manager.update_session(
            session_id,
            request.query,
            intent_result.type,
            intent_result.entities,
            analysis_result,
            response["explanation"]
        )
        
        response["session_id"] = session_id
        
        return QueryResponse(**response)
        
    except Exception as e:
        import traceback
        full_trace = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}\n{full_trace}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "InsightX Conversational AI",
        "version": "1.0.0"
    }

@router.get("/supported-entities")
async def get_supported_entities():
    """Return supported entity types for queries"""
    return {
        "categories": intent_recognizer.categories,
        "devices": intent_recognizer.devices,
        "networks": intent_recognizer.networks,
        "states": intent_recognizer.states,
        "age_groups": intent_recognizer.age_groups,
        "intent_types": ["descriptive", "comparative", "user_segmentation", "risk_analysis"]
    }

@router.get("/example-queries")
async def get_example_queries():
    """Return example queries for guidance"""
    return {
        "examples": [
            {
                "query": "What's the average transaction amount for Food category?",
                "intent": "descriptive"
            },
            {
                "query": "Compare transaction amounts between iOS and Android users",
                "intent": "comparative"
            },
            {
                "query": "Show me transaction patterns by age group",
                "intent": "user_segmentation"
            },
            {
                "query": "What's the fraud rate for Entertainment category?",
                "intent": "risk_analysis"
            },
            {
                "query": "Peak hours for transactions in Maharashtra",
                "intent": "descriptive"
            }
        ]
    }
@router.post("/conversation/start")
async def start_conversation():
    """
    Start a new conversation session.
    Returns session_id to use in subsequent queries for context awareness.
    """
    session_id = conversation_manager.create_session()
    return {
        "session_id": session_id,
        "message": "Conversation started. Use this session_id in future queries for context-aware responses."
    }

@router.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Retrieve conversation history for a session"""
    session = conversation_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    return {
        "session_id": session_id,
        "created_at": session["created_at"],
        "last_updated": session["updated_at"],
        "conversation_history": session["conversation_history"],
        "total_turns": len(session["conversation_history"])
    }

@router.delete("/conversation/{session_id}")
async def end_conversation(session_id: str):
    """End a conversation and clear its context"""
    cleared = conversation_manager.clear_session(session_id)
    if not cleared:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "message": f"Conversation {session_id} has been cleared"
    }

@router.post("/conversation/{session_id}/reset")
async def reset_session(session_id: str):
    """Reset session while keeping the ID (clear history and entities)"""
    session = conversation_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    # Clear history but keep the session
    session["conversation_history"] = []
    session["last_entities"] = {}
    session["extracted_context"] = {}
    session["last_intent"] = None
    
    return {
        "message": f"Session {session_id} has been reset",
        "session_id": session_id
    }