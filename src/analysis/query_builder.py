from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from src.database.models import Transaction
import statistics
from datetime import datetime, timedelta
import re

class QueryBuilder:
    """Builds and executes database queries based on intent"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def execute_query(self, intent_type: str, entities: Dict[str, str], query_text: str = "") -> Dict[str, Any]:
        """
        Execute query based on intent type and extracted entities
        Returns analysis results with statistics and insights
        
        Args:
            intent_type: Type of intent (descriptive, comparative, etc.)
            entities: Extracted entities from NLP
            query_text: Original user query for pattern detection (e.g., "top X")
        """
        if intent_type == "descriptive":
            return self._descriptive_analysis(entities)
        elif intent_type == "comparative":
            return self._comparative_analysis(entities, query_text)
        elif intent_type == "user_segmentation":
            return self._user_segmentation(entities)
        elif intent_type == "risk_analysis":
            return self._risk_analysis(entities)
        else:
            return self._descriptive_analysis(entities)
    
    def _descriptive_analysis(self, entities: Dict[str, str]) -> Dict[str, Any]:
        """Perform descriptive analysis - averages, totals, trends"""
        query = self.db.query(Transaction)
        
        # Apply filters based on entities
        if 'merchant_category' in entities:
            query = query.filter(Transaction.merchant_category == entities['merchant_category'])
        elif 'category' in entities:  # Fallback for old key
            query = query.filter(Transaction.merchant_category == entities['category'])
        
        if 'device_type' in entities:
            query = query.filter(Transaction.device_type == entities['device_type'])
        
        if 'sender_state' in entities:
            query = query.filter(Transaction.sender_state == entities['sender_state'])
        elif 'state' in entities:  # Fallback for old key
            query = query.filter(Transaction.sender_state == entities['state'])
        
        if 'sender_age_group' in entities:
            query = query.filter(Transaction.sender_age_group == entities['sender_age_group'])
        elif 'age_group' in entities:  # Fallback for old key
            query = query.filter(Transaction.sender_age_group == entities['age_group'])
        
        # Get transactions
        transactions = query.all()
        
        if not transactions:
            return {
                "insight": "No transactions found matching the criteria",
                "total_count": 0,
                "statistics": None,
                "success_rate": 0
            }
        
        amounts = [t.amount for t in transactions]
        successful_count = len([t for t in transactions if t.transaction_status == "success"])
        success_rate = (successful_count / len(transactions) * 100) if transactions else 0
        
        return {
            "insight": f"Analyzed {len(transactions)} transactions",
            "total_count": len(transactions),
            "statistics": {
                "total_amount": sum(amounts),
                "average_amount": sum(amounts) / len(amounts),
                "median_amount": statistics.median(amounts),
                "min_amount": min(amounts),
                "max_amount": max(amounts),
                "std_dev": statistics.stdev(amounts) if len(amounts) > 1 else 0,
                "sample_transactions": [(t.transaction_id, t.amount, t.merchant_category, t.timestamp.isoformat()) for t in transactions[:5]]
            },
            "success_rate": success_rate
        }
    
    def _comparative_analysis(self, entities: Dict[str, str], query_text: str = "") -> Dict[str, Any]:
        """
        Compare metrics across different dimensions.
        Handles "top X" queries to show top items/merchants.
        Respects comparison_dimension from NLP (e.g., "state wise comparison")
        """
        
        # Check if this is a "top X" query
        top_count = self._extract_top_count(query_text)
        
        # If asking for top items in a category, show by merchant
        merchant_category = entities.get('merchant_category') or entities.get('category')
        if top_count and merchant_category:
            return self._comparative_by_merchant(entities, top_count)
        
        # Determine comparison dimension
        # Priority: explicit comparison_dimension > default logic
        if 'comparison_dimension' in entities:
            comparison_key = entities['comparison_dimension']
        else:
            # Default: Compare by device type if not specified
            comparison_key = 'device_type'
            if 'device_type' in entities:
                comparison_key = 'network_type'
            elif 'network_type' in entities:
                comparison_key = 'device_type'
        
        # Map old keys to new keys
        key_mapping = {
            'category': 'merchant_category',
            'state': 'sender_state',
            'age_group': 'sender_age_group'
        }
        comparison_key = key_mapping.get(comparison_key, comparison_key)
        
        # Get base filters (don't filter by the comparison dimension)
        base_filters = []
        
        merchant_category = entities.get('merchant_category') or entities.get('category')
        if merchant_category and comparison_key != 'merchant_category':
            base_filters.append(Transaction.merchant_category == merchant_category)
        
        sender_state = entities.get('sender_state') or entities.get('state')
        if sender_state and comparison_key != 'sender_state':
            base_filters.append(Transaction.sender_state == sender_state)
        
        if 'device_type' in entities and comparison_key != 'device_type':
            base_filters.append(Transaction.device_type == entities['device_type'])
        
        sender_age_group = entities.get('sender_age_group') or entities.get('age_group')
        if sender_age_group and comparison_key != 'sender_age_group':
            base_filters.append(Transaction.sender_age_group == sender_age_group)
        
        # Build query based on comparison dimension
        comparison_data = []
        
        if comparison_key == 'sender_state':
            groups = self.db.query(
                Transaction.sender_state,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount')
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(Transaction.sender_state).all()
            
        elif comparison_key == 'merchant_category':
            groups = self.db.query(
                Transaction.merchant_category,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount')
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(Transaction.merchant_category).all()
            
        elif comparison_key == 'sender_age_group':
            groups = self.db.query(
                Transaction.sender_age_group,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount')
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(Transaction.sender_age_group).all()
            
        elif comparison_key == 'network_type':
            groups = self.db.query(
                Transaction.network_type,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount')
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(Transaction.network_type).all()
        
        elif comparison_key == 'transaction_type':
            groups = self.db.query(
                Transaction.transaction_type,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount')
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(Transaction.transaction_type).all()
            
        else:  # device_type (default)
            groups = self.db.query(
                Transaction.device_type,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount')
            )
            for filt in base_filters:
                groups = groups.filter(filt)
            groups = groups.group_by(Transaction.device_type).all()
        
        # Build comparison data
        for group in groups:
            comparison_data.append({
                "category": group[0] if group[0] else "Unknown",
                "transaction_count": group[1],
                "average_amount": float(group[2]) if group[2] else 0,
                "total_amount": float(group[3]) if group[3] else 0
            })
        
        # Sort by average amount (descending)
        comparison_data = sorted(comparison_data, key=lambda x: x['average_amount'], reverse=True)
        
        total_count = sum([d['transaction_count'] for d in comparison_data]) if comparison_data else 0

        return {
            "insight": f"Compared across {comparison_key}",
            "comparison_key": comparison_key,
            "data": comparison_data[:top_count] if top_count else comparison_data,
            "best_performer": comparison_data[0]['category'] if comparison_data else None,
            "total_count": total_count
        }
    
    def _comparative_by_merchant(self, entities: Dict[str, str], top_count: int = 3) -> Dict[str, Any]:
        """Show top merchants/categories by transaction count in a category"""
        
        merchant_category = entities.get('merchant_category') or entities.get('category', '')
        
        # Query top items in this category (ordered by transaction count)
        result = self.db.query(
            Transaction.merchant_category,
            func.count(Transaction.transaction_id).label('transaction_count'),
            func.avg(Transaction.amount).label('average_amount'),
            func.sum(Transaction.amount).label('total_amount')
        ).filter(Transaction.merchant_category == merchant_category)
        
        sender_state = entities.get('sender_state') or entities.get('state')
        if sender_state:
            result = result.filter(Transaction.sender_state == sender_state)
        
        result = result.group_by(
            Transaction.merchant_category
        ).order_by(desc('transaction_count')).limit(top_count).all()
        
        comparison_data = []
        for row in result:
            comparison_data.append({
                "category": row[0] if row[0] else "Unknown",
                "transaction_count": row[1],
                "average_amount": float(row[2]) if row[2] else 0,
                "total_amount": float(row[3]) if row[3] else 0
            })
        
        total_count = sum([d['transaction_count'] for d in comparison_data]) if comparison_data else 0
        
        return {
            "insight": f"Top {top_count} items in {merchant_category}",
            "comparison_key": "merchant_category",
            "data": comparison_data,
            "best_performer": comparison_data[0]['category'] if comparison_data else None,
            "total_count": total_count
        }
    
    def _extract_top_count(self, query_text: str) -> Optional[int]:
        """Extract 'top N' from query text"""
        if not query_text:
            return None
        
        # Look for patterns like "top 3", "top three", "top5"
        match = re.search(r'top\s*(\d+|three|five|ten)', query_text.lower())
        if match:
            count_str = match.group(1)
            if count_str.isdigit():
                return int(count_str)
            else:
                # Convert word to number
                word_to_num = {"three": 3, "five": 5, "ten": 10}
                return word_to_num.get(count_str, 3)
        
        return None
    
    def _user_segmentation(self, entities: Dict[str, str]) -> Dict[str, Any]:
        """Analyze transactions by segment - age, state, category"""
        
        # Determine segmentation key: prefer explicit `segment_by` from NLP
        segment_key = entities.get('segment_by', 'sender_age_group')

        # Normalize common aliases
        if segment_key in ['state', 'states']:
            segment_key = 'sender_state'
        if segment_key in ['category', 'merchant_category']:
            segment_key = 'merchant_category'
        if segment_key in ['age_group']:
            segment_key = 'sender_age_group'
        
        # Build segments
        if segment_key == 'sender_age_group':
            segments = self.db.query(
                Transaction.sender_age_group,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount')
            ).group_by(Transaction.sender_age_group).all()
        elif segment_key == 'sender_state':
            segments = self.db.query(
                Transaction.sender_state,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount')
            ).group_by(Transaction.sender_state).all()
        elif segment_key == 'merchant_category':
            segments = self.db.query(
                Transaction.merchant_category,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount')
            ).group_by(Transaction.merchant_category).all()
        elif segment_key == 'device_type':
            segments = self.db.query(
                Transaction.device_type,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount')
            ).group_by(Transaction.device_type).all()
        elif segment_key == 'network_type':
            segments = self.db.query(
                Transaction.network_type,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount')
            ).group_by(Transaction.network_type).all()
        elif segment_key == 'transaction_type':
            segments = self.db.query(
                Transaction.transaction_type,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount')
            ).group_by(Transaction.transaction_type).all()
        elif segment_key == 'sender_bank':
            segments = self.db.query(
                Transaction.sender_bank,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount')
            ).group_by(Transaction.sender_bank).all()
        else:
            # Default to sender_state
            segments = self.db.query(
                Transaction.sender_state,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount')
            ).group_by(Transaction.sender_state).all()
        
        segment_data = []
        for segment in segments:
            segment_data.append({
                "segment": segment[0] if segment[0] else "Unknown",
                "transaction_count": segment[1],
                "average_transaction_value": float(segment[2]) if segment[2] else 0
            })
        
        total_count = sum([s['transaction_count'] for s in segment_data]) if segment_data else 0

        return {
            "insight": f"Segmented transactions by {segment_key}",
            "segment_key": segment_key,
            "segments": sorted(segment_data, key=lambda x: x['transaction_count'], reverse=True),
            "top_segment": segment_data[0]['segment'] if segment_data else None,
            "total_count": total_count
        }
    
    def _risk_analysis(self, entities: Dict[str, str]) -> Dict[str, Any]:
        """Analyze fraud flags and failed transactions"""
        
        base_query = self.db.query(Transaction)
        
        merchant_category = entities.get('merchant_category') or entities.get('category')
        if merchant_category:
            base_query = base_query.filter(Transaction.merchant_category == merchant_category)
        
        if 'device_type' in entities:
            base_query = base_query.filter(Transaction.device_type == entities['device_type'])
        
        total_transactions = base_query.count()
        
        # Get fraud stats
        fraud_count = base_query.filter(Transaction.fraud_flag == True).count()
        failed_count = base_query.filter(Transaction.transaction_status == "failed").count()
        
        fraud_by_category = self.db.query(
            Transaction.merchant_category,
            func.count(Transaction.transaction_id).label('fraud_count')
        ).filter(Transaction.fraud_flag == True).group_by(Transaction.merchant_category).all()
        
        return {
            "insight": "Risk analysis summary",
            "total_transactions": total_transactions,
            "total_count": total_transactions,
            "fraud_count": fraud_count,
            "fraud_rate_percent": (fraud_count / total_transactions * 100) if total_transactions > 0 else 0,
            "failed_count": failed_count,
            "failure_rate_percent": (failed_count / total_transactions * 100) if total_transactions > 0 else 0,
            "fraud_by_category": [
                {"category": f[0], "fraud_count": f[1]} 
                for f in fraud_by_category
            ],
            "risk_level": "high" if (fraud_count / total_transactions * 100) > 5 else "medium" if (fraud_count / total_transactions * 100) > 2 else "low"
        }
