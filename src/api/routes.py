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
    Process natural language query and return insights
    """
    try:
        # Step 1: Recognize intent and extract entities
        # Support conversation context: request.context may contain a session_id
        session_id = None
        if request.context and isinstance(request.context, dict):
            session_id = request.context.get("session_id")

        # initial entity extraction
        intent_result = intent_recognizer.recognize_intent(request.query)

        # if we have a session and prior entities, merge them (so follow-ups work)
        if session_id:
            merged_entities = conversation_manager.merge_entities(session_id, intent_result.entities)
            intent_result.entities = merged_entities
        
        # Step 2: Build and execute query
        query_builder = QueryBuilder(db)
        analysis_result = query_builder.execute_query(
            intent_result.type,
            intent_result.entities
        )
        
        # Step 3: Generate natural language response
        response = response_generator.generate_response(
            request.query,
            analysis_result,
            intent_result.type
        )

        # ensure we have a session id to return/update
        if not session_id:
            session_id = conversation_manager.create_session()

        conversation_manager.update_session(session_id, intent_result.type, intent_result.entities, analysis_result)
        response["session_id"] = session_id
        
        return QueryResponse(**response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

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
