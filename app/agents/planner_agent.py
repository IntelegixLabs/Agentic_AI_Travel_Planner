"""
Travel Planner Agent using CrewAI
"""

from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
import json

from app.agents.base import BaseAgent
from app.schemas.travel import TravelPlanRequest

logger = logging.getLogger(__name__)


class TravelPlannerAgent(BaseAgent):
    """Agent responsible for overall travel planning coordination"""
    
    def __init__(self):
        super().__init__(
            name="TravelPlanner",
            role="Senior Travel Planning Coordinator",
            goal="Create comprehensive travel plans that optimize for budget, preferences, and user satisfaction",
            backstory="""You are an experienced travel planning coordinator with 15+ years of experience 
            in the travel industry. You excel at analyzing user requirements, coordinating with multiple 
            service providers, and creating detailed travel itineraries that maximize value while staying 
            within budget constraints. You have deep knowledge of various destinations, travel seasons, 
            and can provide expert recommendations for flights, accommodations, and activities."""
        )
    
    def create_travel_plan(self, request: TravelPlanRequest) -> Dict[str, Any]:
        """
        Create a comprehensive travel plan
        
        Args:
            request: Travel plan request
            
        Returns:
            Travel plan details
        """
        try:
            # Calculate trip duration
            duration = (request.end_date - request.start_date).days
            
            # Create task description
            task_description = f"""
            Create a comprehensive travel plan for the following requirements:
            
            Destination: {request.destination}
            Travel Dates: {request.start_date} to {request.end_date} ({duration} days)
            Budget: ${request.budget}
            Travelers: {request.travelers}
            Travel Class: {request.travel_class}
            Hotel Category: {request.hotel_category}
            Additional Preferences: {request.preferences or 'None specified'}
            
            Please provide:
            1. Budget allocation recommendations (flights vs hotels vs activities)
            2. Best time to book recommendations
            3. Destination-specific tips and considerations
            4. Alternative options if budget is tight
            5. Risk factors and contingency plans
            """
            
            result = self.execute_task(task_description)
            
            # Parse and structure the result
            plan_details = {
                "destination": request.destination,
                "duration_days": duration,
                "budget_breakdown": self._extract_budget_breakdown(result, request.budget),
                "recommendations": self._extract_recommendations(result),
                "planning_notes": result,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=24)
            }
            
            logger.info(f"Travel plan created for {request.destination}")
            return plan_details
            
        except Exception as e:
            logger.error(f"Failed to create travel plan: {e}")
            raise
    
    def _extract_budget_breakdown(self, result: str, total_budget: float) -> Dict[str, float]:
        """Extract budget breakdown from agent result"""
        # This is a simplified extraction - in production, you'd use more sophisticated parsing
        breakdown = {
            "flights": total_budget * 0.4,  # 40% for flights
            "hotels": total_budget * 0.45,  # 45% for hotels
            "activities": total_budget * 0.15  # 15% for activities
        }
        return breakdown
    
    def _extract_recommendations(self, result: str) -> List[str]:
        """Extract recommendations from agent result"""
        # Simplified extraction - in production, use NLP to parse structured recommendations
        recommendations = [
            "Book flights 2-3 weeks in advance for best prices",
            "Consider flexible dates for better deals",
            "Check for seasonal events that might affect pricing",
            "Verify visa requirements for the destination"
        ]
        return recommendations
