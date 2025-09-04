"""
Budget Optimization Agent using CrewAI
"""

from typing import Dict, Any, List
import logging
from datetime import datetime
import json

from app.agents.base import BaseAgent
from app.schemas.travel import TravelPlanRequest, FlightOption, HotelOption

logger = logging.getLogger(__name__)


class BudgetOptimizationAgent(BaseAgent):
    """Agent responsible for budget optimization and cost analysis"""
    
    def __init__(self):
        super().__init__(
            name="BudgetOptimizationAgent",
            role="Travel Budget Optimization Specialist",
            goal="Optimize travel costs while maintaining quality and meeting user preferences",
            backstory="""You are a financial travel expert with extensive experience in 
            budget optimization and cost analysis. You understand travel pricing dynamics, 
            seasonal variations, and can identify the best value propositions across 
            different travel components. You excel at balancing cost savings with quality, 
            finding hidden deals, and providing detailed cost breakdowns to help users 
            make informed financial decisions."""
        )
    
    def optimize_budget(self, request: TravelPlanRequest, 
                       flight_options: List[FlightOption], 
                       hotel_options: List[HotelOption]) -> Dict[str, Any]:
        """
        Optimize budget allocation and recommend best options
        
        Args:
            request: Travel plan request
            flight_options: Available flight options
            hotel_options: Available hotel options
            
        Returns:
            Budget optimization results
        """
        try:
            # Create task description
            task_description = f"""
            Optimize the travel budget for the following scenario:
            
            Total Budget: ${request.budget}
            Destination: {request.destination}
            Duration: {(request.end_date - request.start_date).days} days
            Travelers: {request.travelers}
            
            Available Flight Options:
            {json.dumps([{
                'id': f.id,
                'airline': f.airline,
                'price': f.price,
                'duration': f.duration,
                'layovers': f.layovers
            } for f in flight_options], indent=2)}
            
            Available Hotel Options:
            {json.dumps([{
                'id': h.id,
                'name': h.name,
                'total_price': h.total_price,
                'rating': h.rating,
                'amenities': h.amenities
            } for h in hotel_options], indent=2)}
            
            Please provide:
            1. Optimal budget allocation (flights vs hotels vs activities)
            2. Best value combinations that fit within budget
            3. Cost-saving recommendations
            4. Alternative options if budget is exceeded
            5. Risk assessment for different price points
            """
            
            result = self.execute_task(task_description)
            
            # Analyze and rank options
            optimization_results = self._analyze_options(request, flight_options, hotel_options)
            
            logger.info(f"Budget optimization completed for {request.destination}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Failed to optimize budget: {e}")
            raise
    
    def _analyze_options(self, request: TravelPlanRequest, 
                        flight_options: List[FlightOption], 
                        hotel_options: List[HotelOption]) -> Dict[str, Any]:
        """Analyze and rank travel options by value"""
        
        # Sort options by price
        sorted_flights = sorted(flight_options, key=lambda x: x.price)
        sorted_hotels = sorted(hotel_options, key=lambda x: x.total_price)
        
        # Find combinations that fit within budget
        valid_combinations = []
        
        for flight in sorted_flights:
            for hotel in sorted_hotels:
                total_cost = flight.price + hotel.total_price
                if total_cost <= request.budget:
                    remaining_budget = request.budget - total_cost
                    value_score = self._calculate_value_score(flight, hotel, remaining_budget)
                    
                    valid_combinations.append({
                        "flight": flight,
                        "hotel": hotel,
                        "total_cost": total_cost,
                        "remaining_budget": remaining_budget,
                        "value_score": value_score,
                        "budget_utilization": (total_cost / request.budget) * 100
                    })
        
        # Sort by value score
        valid_combinations.sort(key=lambda x: x["value_score"], reverse=True)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(valid_combinations, request.budget)
        
        return {
            "total_combinations": len(valid_combinations),
            "top_combinations": valid_combinations[:5],  # Top 5 options
            "budget_breakdown": self._calculate_budget_breakdown(request.budget),
            "recommendations": recommendations,
            "cost_analysis": self._generate_cost_analysis(valid_combinations)
        }
    
    def _calculate_value_score(self, flight: FlightOption, hotel: HotelOption, 
                              remaining_budget: float) -> float:
        """Calculate value score for a flight-hotel combination"""
        # Simple scoring algorithm - in production, this would be more sophisticated
        
        # Flight score (lower price, fewer layovers = higher score)
        flight_score = 100 - (flight.price / 1000) * 50  # Price factor
        if not flight.layovers:
            flight_score += 20  # Direct flight bonus
        
        # Hotel score (higher rating, more amenities = higher score)
        hotel_score = hotel.rating * 20  # Rating factor
        hotel_score += len(hotel.amenities) * 2  # Amenities factor
        
        # Budget utilization score
        budget_score = min(remaining_budget / 100, 10)  # Remaining budget factor
        
        return (flight_score + hotel_score + budget_score) / 3
    
    def _generate_recommendations(self, combinations: List[Dict], budget: float) -> List[str]:
        """Generate budget optimization recommendations"""
        recommendations = []
        
        if not combinations:
            recommendations.append("No combinations found within budget. Consider increasing budget or adjusting preferences.")
            return recommendations
        
        best_combo = combinations[0]
        
        if best_combo["budget_utilization"] < 70:
            recommendations.append("Consider upgrading to higher quality options - you have budget flexibility.")
        
        if best_combo["remaining_budget"] > 200:
            recommendations.append("Allocate remaining budget for activities, dining, or travel insurance.")
        
        if len(combinations) < 3:
            recommendations.append("Limited options within budget. Consider flexible dates or alternative destinations.")
        
        recommendations.extend([
            "Book flights 2-3 weeks in advance for best prices",
            "Consider package deals for additional savings",
            "Check for seasonal discounts and promotions"
        ])
        
        return recommendations
    
    def _calculate_budget_breakdown(self, total_budget: float) -> Dict[str, float]:
        """Calculate recommended budget breakdown"""
        return {
            "flights": total_budget * 0.4,
            "hotels": total_budget * 0.45,
            "activities": total_budget * 0.10,
            "contingency": total_budget * 0.05
        }
    
    def _generate_cost_analysis(self, combinations: List[Dict]) -> Dict[str, Any]:
        """Generate cost analysis summary"""
        if not combinations:
            return {"error": "No valid combinations found"}
        
        costs = [combo["total_cost"] for combo in combinations]
        
        return {
            "min_cost": min(costs),
            "max_cost": max(costs),
            "avg_cost": sum(costs) / len(costs),
            "cost_range": max(costs) - min(costs),
            "budget_efficiency": len(combinations) / 10 * 100  # Percentage of budget range covered
        }
