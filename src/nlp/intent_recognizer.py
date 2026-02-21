import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Intent:
    type: str  # e.g., "descriptive", "comparative", "user_segmentation", "risk_analysis"
    confidence: float
    entities: Dict[str, str]

class IntentRecognizer:
    """
    Recognizes business intents from natural language queries
    """
    
    def __init__(self):
        self.categories = [
            "Food", "Entertainment", "Travel", "Shopping", "Utilities", 
            "Healthcare", "Education", "Bills", "Downloads", "Other"
        ]
        self.devices = ["iOS", "Android", "Web"]
        self.networks = ["WiFi", "4G", "5G"]
        self.states = [
            "Maharashtra", "Karnataka", "Delhi", "Tamil Nadu", "Telangana",
            "Gujarat", "Rajasthan", "Punjab", "West Bengal", "Uttar Pradesh",
            "Andhra Pradesh", "Haryana", "Madhya Pradesh", "Bihar", "Odisha"
        ]
        self.age_groups = ["13-18", "18-25", "25-35", "35-45", "45-55", "55+"]
        
    def recognize_intent(self, query: str) -> Intent:
        """
        Recognize intent from natural language query
        Returns intent type and extracted entities
        """
        query_lower = query.lower()
        
        # Determine intent type
        intent_type = self._classify_intent(query_lower)
        
        # Extract entities
        entities = self._extract_entities(query_lower)
        
        # Calculate confidence based on entity extraction
        confidence = min(0.95, 0.7 + len(entities) * 0.05)
        
        return Intent(
            type=intent_type,
            confidence=confidence,
            entities=entities
        )
    
    def _classify_intent(self, query: str) -> str:
        """Classify query into intent type"""
        
        # Descriptive analysis patterns
        descriptive_keywords = [
            "average", "mean", "total", "sum", "how much", "peak", "highest",
            "lowest", "most", "least", "analyze", "what are", "what is",
            "trend", "pattern", "distribution"
        ]
        
        # Comparative analysis patterns
        comparative_keywords = [
            "compare", "versus", "vs", "difference", "better", "worse",
            "higher", "lower", "faster", "slower", "more than", "less than",
            "between", "across"
        ]
        
        # User segmentation patterns
        segmentation_keywords = [
            "age group", "state", "region", "segment", "demographic",
            "by age", "by state", "by device", "by network", "users in", "by category"
        ]
        
        # Risk analysis patterns
        risk_keywords = [
            "fraud", "risk", "failed", "failure rate", "flagged", "suspicious",
            "anomaly", "unusual", "suspicious", "problem"
        ]
        
        # Priority ordering: risk -> comparative -> segmentation -> descriptive
        for keyword in risk_keywords:
            if keyword in query:
                return "risk_analysis"

        for keyword in comparative_keywords:
            if keyword in query:
                return "comparative"

        for keyword in segmentation_keywords:
            if keyword in query:
                return "user_segmentation"

        for keyword in descriptive_keywords:
            if keyword in query:
                return "descriptive"

        return "descriptive"  # Default
    
    def _extract_entities(self, query: str) -> Dict[str, str]:
        """Extract entities like category, device, state, etc."""
        entities = {}
        
        # Extract categories
        for category in self.categories:
            if category.lower() in query:
                entities['category'] = category
                break
        
        # Extract devices
        for device in self.devices:
            if device.lower() in query:
                entities['device_type'] = device
                break
        
        # Extract networks
        for network in self.networks:
            if network.lower() in query:
                entities['network_type'] = network
                break
        
        # Extract states
        for state in self.states:
            if state.lower() in query:
                entities['state'] = state
                break
        
        # Extract age groups
        for age_group in self.age_groups:
            if age_group in query:
                entities['age_group'] = age_group
                break
        
        # Extract time references
        time_ref = self._extract_time_reference(query)
        if time_ref:
            entities['time_reference'] = time_ref

        # Detect explicit segmentation requests like "by state", "by age", "age group"
        seg_match = re.search(r"\bby (state|age|category|device|network)\b", query)
        if seg_match:
            val = seg_match.group(1)
            if val == 'age':
                entities['segment_by'] = 'age_group'
            elif val == 'device':
                entities['segment_by'] = 'device_type'
            elif val == 'network':
                entities['segment_by'] = 'network_type'
            else:
                entities['segment_by'] = val

        # Also handle phrases like "age group" or "by age group"
        if 'age group' in query:
            entities['segment_by'] = 'age_group'
        if 'by state' in query or 'by states' in query or 'transaction patterns by state' in query:
            entities['segment_by'] = 'state'
        
        return entities
    
    def _extract_time_reference(self, query: str) -> Optional[str]:
        """Extract time reference from query"""
        time_patterns = {
            "today": "today",
            "yesterday": "yesterday",
            "this week": "week",
            "this month": "month",
            "this year": "year",
            "last week": "last_week",
            "last month": "last_month",
            "morning": "morning",
            "afternoon": "afternoon",
            "evening": "evening",
            "night": "night",
            "peak": "peak_hours"
        }
        
        for pattern, label in time_patterns.items():
            if pattern in query:
                return label
        
        return None
