from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from src.database.models import Transaction
import statistics
from datetime import datetime, timedelta

class QueryBuilder:
    """Builds and executes database queries based on intent"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def execute_query(self, intent_type: str, entities: Dict[str, str]) -> Dict[str, Any]:
        """
        Execute query based on intent type and extracted entities
        Returns analysis results with statistics and insights
        """
        if intent_type == "descriptive":
            return self._descriptive_analysis(entities)
        elif intent_type == "comparative":
            return self._comparative_analysis(entities)
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
        if 'category' in entities:
            query = query.filter(Transaction.category == entities['category'])
        
        if 'device_type' in entities:
            query = query.filter(Transaction.device_type == entities['device_type'])
        
        if 'state' in entities:
            query = query.filter(Transaction.state == entities['state'])
        
        if 'age_group' in entities:
            query = query.filter(Transaction.age_group == entities['age_group'])
        
        # Get transactions
        transactions = query.all()
        
        if not transactions:
            return {
                "insight": "No transactions found matching the criteria",
                "total_count": 0,
                "statistics": None
            }
        
        amounts = [t.amount for t in transactions]
        
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
                "sample_transactions": [(t.transaction_id, t.amount, t.category, t.timestamp.isoformat()) for t in transactions[:5]]
            },
            "success_rate": len([t for t in transactions if t.status == "success"]) / len(transactions) * 100
        }
    
    def _comparative_analysis(self, entities: Dict[str, str]) -> Dict[str, Any]:
        """Compare metrics across different dimensions"""
        
        # Compare by device type if not specified
        comparison_key = 'device_type'
        if 'device_type' in entities:
            comparison_key = 'network_type'
        elif 'network_type' in entities:
            comparison_key = 'device_type'
        
        # Get base query
        base_query = self.db.query(Transaction)
        
        if 'category' in entities:
            base_query = base_query.filter(Transaction.category == entities['category'])
        if 'state' in entities:
            base_query = base_query.filter(Transaction.state == entities['state'])
        
        # Group by comparison key
        if comparison_key == 'device_type':
            groups = self.db.query(
                Transaction.device_type,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount')
            ).group_by(Transaction.device_type).all()
        else:
            groups = self.db.query(
                Transaction.network_type,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_amount')
            ).group_by(Transaction.network_type).all()
        
        comparison_data = []
        for group in groups:
            comparison_data.append({
                "category": group[0] if group[0] else "Unknown",
                "transaction_count": group[1],
                "average_amount": float(group[2]) if group[2] else 0,
                "total_amount": float(group[3]) if group[3] else 0
            })
        
        total_count = sum([d['transaction_count'] for d in comparison_data]) if comparison_data else 0

        return {
            "insight": f"Compared across {comparison_key}",
            "comparison_key": comparison_key,
            "data": comparison_data,
            "best_performer": max(comparison_data, key=lambda x: x['average_amount'])['category'] if comparison_data else None,
            "total_count": total_count
        }
    
    def _user_segmentation(self, entities: Dict[str, str]) -> Dict[str, Any]:
        """Analyze users by segment - age, state, category"""
        
        # Determine segmentation key: prefer explicit `segment_by` from NLP
        segment_key = entities.get('segment_by', 'age_group')

        # Normalize common aliases
        if segment_key in ['state', 'states']:
            segment_key = 'state'
        if segment_key in ['category', 'merchant_category']:
            segment_key = 'category'
        
        # Build segments
        if segment_key == 'age_group':
            segments = self.db.query(
                Transaction.age_group,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.count(func.distinct(Transaction.user_id)).label('unique_users')
            ).group_by(Transaction.age_group).all()
        elif segment_key == 'state':
            segments = self.db.query(
                Transaction.state,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.count(func.distinct(Transaction.user_id)).label('unique_users')
            ).group_by(Transaction.state).all()
        elif segment_key == 'category':
            segments = self.db.query(
                Transaction.category,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.count(func.distinct(Transaction.user_id)).label('unique_users')
            ).group_by(Transaction.category).all()
        elif segment_key == 'device_type':
            segments = self.db.query(
                Transaction.device_type,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.count(func.distinct(Transaction.user_id)).label('unique_users')
            ).group_by(Transaction.device_type).all()
        elif segment_key == 'network_type':
            segments = self.db.query(
                Transaction.network_type,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.count(func.distinct(Transaction.user_id)).label('unique_users')
            ).group_by(Transaction.network_type).all()
        else:
            segments = self.db.query(
                Transaction.state,
                func.count(Transaction.transaction_id).label('count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.count(func.distinct(Transaction.user_id)).label('unique_users')
            ).group_by(Transaction.state).all()
        
        segment_data = []
        for segment in segments:
            segment_data.append({
                "segment": segment[0] if segment[0] else "Unknown",
                "transaction_count": segment[1],
                "average_transaction_value": float(segment[2]) if segment[2] else 0,
                "unique_users": segment[3]
            })
        
        total_count = sum([s['transaction_count'] for s in segment_data]) if segment_data else 0

        return {
            "insight": f"Segmented users by {segment_key}",
            "segment_key": segment_key,
            "segments": sorted(segment_data, key=lambda x: x['transaction_count'], reverse=True),
            "top_segment": segment_data[0]['segment'] if segment_data else None,
            "total_count": total_count
        }
    
    def _risk_analysis(self, entities: Dict[str, str]) -> Dict[str, Any]:
        """Analyze fraud flags and failed transactions"""
        
        base_query = self.db.query(Transaction)
        
        if 'category' in entities:
            base_query = base_query.filter(Transaction.category == entities['category'])
        if 'device_type' in entities:
            base_query = base_query.filter(Transaction.device_type == entities['device_type'])
        
        total_transactions = base_query.count()
        
        # Get fraud stats
        fraud_count = base_query.filter(Transaction.fraud_flag == True).count()
        failed_count = base_query.filter(Transaction.status == "failed").count()
        
        fraud_by_category = self.db.query(
            Transaction.category,
            func.count(Transaction.transaction_id).label('fraud_count')
        ).filter(Transaction.fraud_flag == True).group_by(Transaction.category).all()
        
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
