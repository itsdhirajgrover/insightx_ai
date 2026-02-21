import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class ResponseGenerator:
    """
    Generates natural language responses from data analysis results
    Uses LLM for conversational and explainable outputs
    """
    
    def __init__(self):
        try:
            import openai
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set")
            openai.api_key = self.openai_api_key
            self.client = openai
            self.use_llm = True
        except Exception as e:
            print(f"Warning: LLM integration not available: {e}")
            self.use_llm = False
    
    def generate_response(self, query: str, analysis_result: Dict[str, Any], intent_type: str) -> Dict[str, Any]:
        """
        Generate conversational response from analysis results
        Returns explanation, insights, and recommendations
        """
        
        # Extract key insights
        insights = self._extract_insights(analysis_result, intent_type)
        
        # Generate explanation
        if self.use_llm:
            explanation = self._generate_llm_response(query, analysis_result, intent_type, insights)
        else:
            explanation = self._generate_template_response(analysis_result, intent_type, insights)
        
        return {
            "query": query,
            "intent": intent_type,
            "explanation": explanation,
            "insights": insights,
            "raw_data": analysis_result,
            "confidence_score": self._calculate_confidence(analysis_result)
        }
    
    def _extract_insights(self, result: Dict[str, Any], intent_type: str) -> list:
        """Extract key insights from analysis result"""
        insights = []
        
        if intent_type == "descriptive":
            if "statistics" in result and result["statistics"]:
                stats = result["statistics"]
                insights.append(f"Total transactions analyzed: {result.get('total_count', 0)}")
                if "average_amount" in stats:
                    insights.append(f"Average transaction amount: ₹{stats['average_amount']:.2f}")
                if "total_amount" in stats:
                    insights.append(f"Total transaction value: ₹{stats['total_amount']:.2f}")
                insights.append(f"Success rate: {result.get('success_rate', 0):.2f}%")
        
        elif intent_type == "comparative":
            if "data" in result:
                insights.append(f"Comparison across: {result.get('comparison_key', 'categories')}")
                for item in result['data'][:3]:
                    insights.append(f"{item['category']}: ₹{item['average_amount']:.2f} avg, {item['transaction_count']} transactions")
        
        elif intent_type == "user_segmentation":
            if "segments" in result:
                top_segment = result['segments'][0] if result['segments'] else None
                if top_segment:
                    insights.append(f"Top segment: {top_segment['segment']} with {top_segment['transaction_count']} transactions")
                insights.append(f"Segmentation by: {result.get('segment_key', 'segment')}")
        
        elif intent_type == "risk_analysis":
            insights.append(f"Fraud rate: {result.get('fraud_rate_percent', 0):.2f}%")
            insights.append(f"Failure rate: {result.get('failure_rate_percent', 0):.2f}%")
            insights.append(f"Risk level: {result.get('risk_level', 'unknown').upper()}")
        
        return insights
    
    def _generate_llm_response(self, user_query: str, analysis_result: Dict[str, Any], intent_type: str, insights: list) -> str:
        """Generate response using LLM with fallback to template"""
        try:
            prompt = f"""
You are a financial data analyst AI. Based on the following analysis results, provide a clear, concise, and actionable response to the user's query.

User Query: {user_query}
Intent Type: {intent_type}
Key Insights: {json.dumps(insights)}
Detailed Analysis: {json.dumps(analysis_result, indent=2, default=str)}

Please provide:
1. A direct answer to the user's question
2. Supporting statistics and trends
3. One key recommendation based on the data

Keep the response focused, professional, and easy to understand for non-technical stakeholders.
"""
            
            # Note: This requires actual OpenAI API integration
            # For now, falling back to template
            return self._generate_template_response(analysis_result, intent_type, insights)
            
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._generate_template_response(analysis_result, intent_type, insights)
    
    def _generate_template_response(self, result: Dict[str, Any], intent_type: str, insights: list) -> str:
        """Generate response using templates"""
        
        if intent_type == "descriptive":
            return self._template_descriptive(result, insights)
        elif intent_type == "comparative":
            return self._template_comparative(result, insights)
        elif intent_type == "user_segmentation":
            return self._template_segmentation(result, insights)
        elif intent_type == "risk_analysis":
            return self._template_risk(result, insights)
        else:
            return "Analysis complete. See insights for details."
    
    def _template_descriptive(self, result: Dict[str, Any], insights: list) -> str:
        stats = result.get("statistics", {})
        response = "**Descriptive Summary**\n\n"

        # Key overview
        total = result.get('total_count', 0)
        response += f"- **Total transactions analyzed:** {total:,}\n"

        # Core statistics
        if "average_amount" in stats:
            response += f"- **Average transaction amount:** ₹{stats['average_amount']:,.2f}\n"
        if "median_amount" in stats:
            response += f"- **Median transaction amount:** ₹{stats['median_amount']:,.2f}\n"
        if "total_amount" in stats:
            response += f"- **Total transaction value:** ₹{stats['total_amount']:,.2f}\n"

        # Success / rates
        response += f"- **Success rate:** {result.get('success_rate', 0):.2f}%\n"

        # Range and sample insights
        if stats.get('min_amount') is not None and stats.get('max_amount') is not None:
            response += f"- **Range:** ₹{stats.get('min_amount', 0):,.2f} — ₹{stats.get('max_amount', 0):,.2f}\n"

        # Add top insights (concise)
        if insights:
            response += "\n**Key insights:**\n"
            for insight in insights[:3]:
                response += f"- {insight}\n"

        return response
    
    def _template_comparative(self, result: Dict[str, Any], insights: list) -> str:
        # Build a clean, tabular-style comparative summary
        key = result.get('comparison_key', 'dimensions')
        title = key.replace('_', ' ').title() + ' Comparison'
        response = f"**{title}**\n\n"
        response += f"- **Scope:** `{key}`\n"

        data = result.get('data', [])
        if data:
            for item in data:
                name = item.get('category') or item.get('segment') or item.get('name') or 'Unknown'
                avg = item.get('average_amount', 0.0)
                count = item.get('transaction_count', 0)
                response += f"- **{name}:** Average = ₹{avg:,.2f}; Transactions = {count:,}\n"

        # Add best performer insight if available
        if result.get('best_performer'):
            response += f"\n- **Insight:** {result['best_performer']} shows the highest average transaction value, indicating strong performance in this segment."

        return response
    
    def _template_segmentation(self, result: Dict[str, Any], insights: list) -> str:
        key = result.get('segment_key', 'segment')
        response = f"**User Segmentation by {key.replace('_',' ').title()}**\n\n"

        # Brief summary
        if result.get('total_count') is not None:
            response += f"- **Total transactions analyzed:** {result.get('total_count',0):,}\n"

        # Add short insights
        if insights:
            response += "\n**Key insights:**\n"
            for insight in insights[:4]:
                response += f"- {insight}\n"

        # Detailed top segments
        segments = result.get('segments', [])
        if segments:
            response += "\n**Top segments by transaction volume:**\n"
            for seg in segments[:5]:
                seg_name = seg.get('segment') or seg.get('name') or 'Unknown'
                count = seg.get('transaction_count', 0)
                avg = seg.get('average_transaction_value') or seg.get('average_amount') or 0.0
                response += f"- {seg_name}: {count:,} transactions, ₹{avg:,.2f} avg value\n"

        return response
    
    def _template_risk(self, result: Dict[str, Any], insights: list) -> str:
        response = "**Risk Analysis Summary**\n\n"

        # Core metrics
        if 'fraud_rate_percent' in result:
            response += f"- **Fraud rate:** {result.get('fraud_rate_percent',0):.2f}%\n"
        if 'failure_rate_percent' in result:
            response += f"- **Failure rate:** {result.get('failure_rate_percent',0):.2f}%\n"
        response += f"- **Risk level:** {result.get('risk_level','unknown').upper()}\n"

        # Insights
        if insights:
            response += "\n**Key insights:**\n"
            for insight in insights:
                response += f"- {insight}\n"

        # Fraud-by-category details
        fraud_categories = result.get('fraud_by_category', [])
        if fraud_categories:
            response += "\n**Categories with highest fraud concerns:**\n"
            for item in fraud_categories[:5]:
                response += f"- {item.get('category','Unknown')}: {item.get('fraud_count',0):,} flagged transactions\n"

        # Recommendations
        risk_level = (result.get('risk_level') or 'unknown').lower()
        recommendations = {
            "high": "Immediate action required — review fraud detection and implement stricter verification.",
            "medium": "Monitor transactions closely — consider enhancing security measures for high-risk categories.",
            "low": "Current fraud rates are acceptable — continue monitoring and maintain existing controls."
        }
        response += f"\n**Recommendation:** {recommendations.get(risk_level, 'Review security protocols and investigate anomalies.')}\n"

        return response
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score based on result completeness"""
        score = 0.8  # Base score
        
        if result.get('total_count', 0) > 100:
            score += 0.1
        elif result.get('total_count', 0) < 10:
            score -= 0.2
        
        # Bonus for rich insight data
        if result.get('statistics') or result.get('data') or result.get('segments'):
            score += 0.05
        
        return min(0.98, max(0.6, score))
