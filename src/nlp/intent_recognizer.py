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
    Enhanced to recognize entities from actual database schema:
    - merchant_category (merchants)
    - sender_state, receiver_state
    - sender_age_group, receiver_age_group
    - transaction_type, transaction_status
    - sender_bank, receiver_bank
    - device_type, network_type
    - temporal: hour_of_day, day_of_week, is_weekend
    """
    
    def __init__(self):
        # Merchant categories from data
        self.merchant_categories = [
            "Food", "Entertainment", "Travel", "Shopping", "Utilities", 
            "Healthcare", "Education", "Bills", "Downloads", "Other", "Groceries",
            "Restaurants", "Hotels", "Airlines", "Retail", "Services"
        ]
        
        self.transaction_types = [
            "P2P", "Merchant", "Bill", "Recharge", "Investment",
            "Withdrawal", "Transfer", "Subscription"
        ]
        
        self.devices = ["iOS", "Android", "Web", "USSD"]
        
        self.networks = ["WiFi", "4G", "5G", "3G", "2G"]
        
        self.states = [
            "Maharashtra", "Karnataka", "Delhi", "Tamil Nadu", "Telangana",
            "Gujarat", "Rajasthan", "Punjab", "West Bengal", "Uttar Pradesh",
            "Andhra Pradesh", "Haryana", "Madhya Pradesh", "Bihar", "Odisha",
            "Jharkhand", "Uttarakhand", "Himachal Pradesh", "Assam", "Kerala"
        ]
        
        self.age_groups = ["13-18", "18-25", "25-35", "35-45", "45-55", "55+"]
        
        self.banks = [
            "HDFC", "ICIC", "SBI", "Axis", "IDBI", "PNB", "BOB", "Union",
            "Kotak", "IndusInd", "YES", "ICIC", "RBL", "Federal", "Airtel",
            "Google Pay", "PhonePe", "Paytm", "Amazon Pay"
        ]
        
        self.transaction_statuses = ["Success", "Failed", "Pending", "Declined", "Timeout"]
        
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
    
    def recognize_intent_with_context(self, query: str, conversation_context: Optional[Dict[str, str]] = None) -> Intent:
        """
        Recognize intent with conversation context for follow-up questions.
        Use previous entities to fill in missing context in follow-ups.
        
        Example:
        - Q1: "What's the avg transaction in Food category?"
        - Q2: "How about Entertainment?" -> Uses 'category' context from Q1
        """
        initial_intent = self.recognize_intent(query)
        
        # If we have conversation context, fill missing entities from it
        if conversation_context:
            # Check for follow-up patterns that reference previous context
            if self._is_followup_question(query):
                # Inherit entities from context unless explicitly overridden
                for key, value in conversation_context.items():
                    if key not in initial_intent.entities and value:
                        initial_intent.entities[key] = value
        
        return initial_intent
    
    def _is_followup_question(self, query: str) -> bool:
        """
        Detect if this is a follow-up question that might need context.
        Identifies patterns like "how about", "what about", "compare with", etc.
        """
        followup_patterns = [
            "how about", "what about", "and", "compared to", "vs", "versus",
            "like", "similar", "different", "another", "other", "then what",
            "what else", "any other", "more details", "tell me more",
            "break it down", "segment", "split", "separately"
        ]
        
        query_lower = query.lower()
        for pattern in followup_patterns:
            if pattern in query_lower:
                return True
        
        return False
    
    def _classify_intent(self, query: str) -> str:
        """Classify query into intent type"""
        
        query_lower = query.lower()
        
        # Risk analysis patterns (highest priority)
        risk_keywords = [
            "fraud", "risk", "failed", "failure rate", "flagged", "suspicious",
            "anomaly", "unusual", "suspicious", "problem"
        ]
        
        # Comparative analysis patterns - INCLUDES "TOP X" QUERIES
        comparative_keywords = [
            "compare", "comparison", "versus", "vs", "difference", "better", "worse",
            "higher", "lower", "faster", "slower", "more than", "less than",
            "between", "across", "top", "top 3", "top 5", "top 10",
            "best", "worst", "highest", "lowest", "ranking", "ranked"
        ]
        
        # Segmentation patterns
        segmentation_keywords = [
            "age group", "state", "region", "segment", "demographic",
            "by age", "by state", "by device", "by network", "users in", "by category"
        ]
        
        # Descriptive analysis patterns
        descriptive_keywords = [
            "average", "mean", "total", "sum", "how much", "peak",
            "least", "analyze", "what are", "what is",
            "trend", "pattern", "distribution"
        ]
        
        # Priority ordering: risk -> comparative -> segmentation -> descriptive
        for keyword in risk_keywords:
            if keyword in query_lower:
                return "risk_analysis"

        for keyword in comparative_keywords:
            if keyword in query_lower:
                return "comparative"

        for keyword in segmentation_keywords:
            if keyword in query_lower:
                return "user_segmentation"

        for keyword in descriptive_keywords:
            if keyword in query_lower:
                return "descriptive"

        return "descriptive"  # Default
    
    def _extract_entities(self, query: str) -> Dict[str, str]:
        """
        Extract entities from query based on real database schema:
        - merchant_category, transaction_type, transaction_status
        - sender_state, receiver_state, sender_age_group, receiver_age_group
        - sender_bank, receiver_bank, device_type, network_type
        - temporal: hour_of_day, day_of_week, is_weekend
        """
        entities = {}
        query_lower = query.lower()
        
        # Extract merchant categories
        for category in self.merchant_categories:
            if category.lower() in query_lower:
                entities['merchant_category'] = category
                break
        
        # Extract transaction types
        for tx_type in self.transaction_types:
            if tx_type.lower() in query_lower:
                entities['transaction_type'] = tx_type
                break
        
        # Extract transaction status
        for status in self.transaction_statuses:
            if status.lower() in query_lower:
                entities['transaction_status'] = status
                break
        
        # Extract devices
        for device in self.devices:
            if device.lower() in query_lower:
                entities['device_type'] = device
                break
        
        # Extract networks
        for network in self.networks:
            if network.lower() in query_lower:
                entities['network_type'] = network
                break
        
        # Extract sender state and age group
        for state in self.states:
            if f"sender in {state.lower()}" in query_lower or f"sender from {state.lower()}" in query_lower:
                entities['sender_state'] = state
            if f"{state.lower()} sender" in query_lower:
                entities['sender_state'] = state
        
        # Extract receiver state and age group  
        for state in self.states:
            if f"receiver in {state.lower()}" in query_lower or f"receiver from {state.lower()}" in query_lower:
                entities['receiver_state'] = state
            if f"{state.lower()} receiver" in query_lower:
                entities['receiver_state'] = state
        
        # If just "state" mentioned without sender/receiver context
        for state in self.states:
            if state.lower() in query_lower and 'sender_state' not in entities and 'receiver_state' not in entities:
                entities['state'] = state  # Generic state (will be used as filter)
                break
        
        # Extract sender age group
        for age_group in self.age_groups:
            if f"sender age {age_group}" in query_lower or f"sender {age_group}" in query_lower:
                entities['sender_age_group'] = age_group
        
        # Extract receiver age group
        for age_group in self.age_groups:
            if f"receiver age {age_group}" in query_lower or f"receiver {age_group}" in query_lower:
                entities['receiver_age_group'] = age_group
        
        # If just age mentioned without sender/receiver context
        for age_group in self.age_groups:
            if age_group in query_lower and 'sender_age_group' not in entities and 'receiver_age_group' not in entities:
                entities['age_group'] = age_group  # Generic age group
                break
        
        # Extract banks
        # Bank mention handling: detect "to <bank>", "from <bank>", or explicit sender/receiver
        for bank in self.banks:
            bk_l = bank.lower()
            # explicit patterns
            if re.search(rf"\bto\s+{re.escape(bk_l)}\b", query_lower):
                entities['receiver_bank'] = bank
                break
            if re.search(rf"\bfrom\s+{re.escape(bk_l)}\b", query_lower):
                entities['sender_bank'] = bank
                break
            if bk_l in query_lower:
                if "sender" in query_lower:
                    entities['sender_bank'] = bank
                elif "receiver" in query_lower or "to " in query_lower:
                    entities['receiver_bank'] = bank
                else:
                    entities['bank'] = bank
                break
        
        # Extract temporal references
        time_ref = self._extract_time_reference(query_lower)
        if time_ref:
            entities['time_reference'] = time_ref

        # Handle "to <state>" and "from <state>" patterns for sender/receiver
        for state in self.states:
            s_low = state.lower()
            if re.search(rf"\bto\s+{re.escape(s_low)}\b", query_lower) or re.search(rf"transactions to {re.escape(s_low)}", query_lower) or re.search(rf"sent to {re.escape(s_low)}", query_lower):
                entities['receiver_state'] = state
            if re.search(rf"\bfrom\s+{re.escape(s_low)}\b", query_lower) or re.search(rf"transactions from {re.escape(s_low)}", query_lower) or re.search(rf"sent from {re.escape(s_low)}", query_lower):
                entities['sender_state'] = state
        
        # Extract hour patterns
        hour_match = re.search(r'(\d{1,2})\s*(?:am|pm|:00|o\'clock|hours?)', query_lower)
        if hour_match:
            entities['hour_of_day'] = hour_match.group(1)
        
        # Extract day patterns
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days:
            if day in query_lower:
                entities['day_of_week'] = day
                break
        
        # Extract weekend patterns
        if any(pattern in query_lower for pattern in ["weekend", "saturday", "sunday", "weekends"]):
            entities['is_weekend'] = "true"
        
        # Extract comparison dimension for "X wise" patterns
        wise_match = re.search(r"\b(state|age|category|device|network|bank|status|type)\s+wise\b", query_lower)
        if wise_match:
            val = wise_match.group(1)
            conversion = {
                'age': 'age_group',
                'category': 'merchant_category',
                'device': 'device_type',
                'network': 'network_type',
                'bank': 'sender_bank',
                'status': 'transaction_status',
                'type': 'transaction_type'
            }
            entities['comparison_dimension'] = conversion.get(val, val)
            return entities

        # Detect explicit segmentation requests like "by state", "by age", etc.
        seg_keywords = ["by state", "by age", "by category", "by device", "by network", "by bank", "by status", "by type"]
        for seg_kw in seg_keywords:
            if seg_kw in query_lower:
                if any(kw in query_lower for kw in ["compare", "comparison", "versus", "vs"]):
                    # It's a comparison
                    dim_map = {
                        "by state": "state",
                        "by age": "age_group",
                        "by category": "merchant_category",
                        "by device": "device_type",
                        "by network": "network_type",
                        "by bank": "sender_bank",
                        "by status": "transaction_status",
                        "by type": "transaction_type"
                    }
                    entities['comparison_dimension'] = dim_map.get(seg_kw, seg_kw)
                else:
                    # It's a segmentation
                    seg_map = {
                        "by state": "state",
                        "by age": "age_group",
                        "by category": "merchant_category",
                        "by device": "device_type",
                        "by network": "network_type",
                        "by bank": "sender_bank",
                        "by status": "transaction_status",
                        "by type": "transaction_type"
                    }
                    entities['segment_by'] = seg_map.get(seg_kw, seg_kw)
                break
        
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
            "peak hours": "peak_hours",
            "peak": "peak_hours",
            "office hours": "office_hours",
            "business hours": "business_hours",
            "weekend": "weekend",
            "weekday": "weekday",
            "daytime": "daytime",
            "nighttime": "nighttime"
        }
        
        for pattern, label in time_patterns.items():
            if pattern in query:
                return label
        
        return None
