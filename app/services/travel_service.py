"""
Travel planning service
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.schemas.travel import TravelPlanRequest, TravelPlan, FlightOption, HotelOption
from app.agents.planner_agent import TravelPlannerAgent
from app.agents.flight_agent import FlightBookingAgent
from app.agents.hotel_agent import HotelBookingAgent
from app.agents.budget_agent import BudgetOptimizationAgent
from app.services.flight_clients import FlightService
from app.services.hotel_clients import HotelService
from app.models.travel_plan import TravelPlan as TravelPlanModel

logger = logging.getLogger(__name__)


class TravelService:
    """Service for travel planning operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.planner_agent = TravelPlannerAgent()
        self.flight_agent = FlightBookingAgent()
        self.hotel_agent = HotelBookingAgent()
        self.budget_agent = BudgetOptimizationAgent()
        self.flight_service = FlightService()
        self.hotel_service = HotelService()
    
    async def create_travel_plan(self, request: TravelPlanRequest) -> TravelPlan:
        """
        Create a comprehensive travel plan
        
        Args:
            request: Travel plan request
            
        Returns:
            Complete travel plan
        """
        try:
            logger.info(f"Creating travel plan for {request.destination}")
            
            # Generate unique plan ID
            plan_id = str(uuid.uuid4())
            
            # Use planner agent to create initial plan
            plan_details = self.planner_agent.create_travel_plan(request)
            
            # Search flights and hotels concurrently
            flight_task = self._search_flights(request)
            hotel_task = self._search_hotels(request)
            
            flight_options, hotel_options = await asyncio.gather(flight_task, hotel_task)
            
            # Optimize budget with all options
            budget_optimization = self.budget_agent.optimize_budget(
                request, flight_options, hotel_options
            )
            
            # Calculate total cost from best combination
            best_combination = budget_optimization.get("top_combinations", [{}])[0]
            total_cost = best_combination.get("total_cost", 0)
            
            # Create travel plan
            travel_plan = TravelPlan(
                plan_id=plan_id,
                request=request,
                total_cost=total_cost,
                budget_utilization=(total_cost / request.budget) * 100,
                flight_options=flight_options,
                hotel_options=hotel_options,
                recommendations=budget_optimization.get("recommendations", []),
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            logger.info(f"Travel plan created successfully: {plan_id}")
            return travel_plan
            
        except Exception as e:
            logger.error(f"Failed to create travel plan: {e}")
            raise
    
    async def _search_flights(self, request: TravelPlanRequest) -> List[FlightOption]:
        """Search for flight options"""
        try:
            # For now, use mock data from flight agent
            # In production, this would use the flight service with real APIs
            flight_options = self.flight_agent.search_flights(request)
            
            # Also search external APIs
            external_flights = await self.flight_service.search_all_providers(
                origin="NYC",  # Mock origin
                destination=request.destination,
                departure_date=request.start_date,
                return_date=request.end_date,
                travelers=request.travelers,
                travel_class=request.travel_class
            )
            
            # Combine and deduplicate
            all_flights = flight_options + external_flights
            unique_flights = self._deduplicate_flights(all_flights)
            
            return unique_flights[:10]  # Return top 10 options
            
        except Exception as e:
            logger.error(f"Flight search failed: {e}")
            return []
    
    async def _search_hotels(self, request: TravelPlanRequest) -> List[HotelOption]:
        """Search for hotel options"""
        try:
            # For now, use mock data from hotel agent
            hotel_options = self.hotel_agent.search_hotels(request)
            
            # Also search external APIs
            external_hotels = await self.hotel_service.search_all_providers(
                destination=request.destination,
                check_in=request.start_date,
                check_out=request.end_date,
                travelers=request.travelers,
                hotel_category=request.hotel_category
            )
            
            # Combine and deduplicate
            all_hotels = hotel_options + external_hotels
            unique_hotels = self._deduplicate_hotels(all_hotels)
            
            return unique_hotels[:10]  # Return top 10 options
            
        except Exception as e:
            logger.error(f"Hotel search failed: {e}")
            return []
    
    def _deduplicate_flights(self, flights: List[FlightOption]) -> List[FlightOption]:
        """Remove duplicate flights based on airline and flight number"""
        seen = set()
        unique_flights = []
        
        for flight in flights:
            key = (flight.airline, flight.flight_number)
            if key not in seen:
                seen.add(key)
                unique_flights.append(flight)
        
        return unique_flights
    
    def _deduplicate_hotels(self, hotels: List[HotelOption]) -> List[HotelOption]:
        """Remove duplicate hotels based on name and address"""
        seen = set()
        unique_hotels = []
        
        for hotel in hotels:
            key = (hotel.name.lower(), hotel.address.lower())
            if key not in seen:
                seen.add(key)
                unique_hotels.append(hotel)
        
        return unique_hotels
    
    async def store_plan(self, plan: TravelPlan) -> None:
        """Store travel plan in database"""
        try:
            db_plan = TravelPlanModel(
                id=plan.plan_id,
                destination=plan.request.destination,
                start_date=plan.request.start_date,
                end_date=plan.request.end_date,
                budget=plan.request.budget,
                travelers=plan.request.travelers,
                travel_class=plan.request.travel_class.value,
                hotel_category=plan.request.hotel_category.value,
                preferences=plan.request.preferences,
                total_cost=plan.total_cost,
                budget_utilization=plan.budget_utilization,
                flight_options=[flight.dict() for flight in plan.flight_options],
                hotel_options=[hotel.dict() for hotel in plan.hotel_options],
                recommendations=plan.recommendations,
                expires_at=plan.expires_at
            )
            
            self.db.add(db_plan)
            await self.db.commit()
            
            logger.info(f"Travel plan stored in database: {plan.plan_id}")
            
        except Exception as e:
            logger.error(f"Failed to store travel plan: {e}")
            await self.db.rollback()
            raise
    
    async def get_travel_plan(self, plan_id: str) -> Optional[TravelPlan]:
        """Get travel plan from database"""
        try:
            result = await self.db.execute(
                select(TravelPlanModel).where(TravelPlanModel.id == plan_id)
            )
            db_plan = result.scalar_one_or_none()
            
            if not db_plan:
                return None
            
            # Convert database model to Pydantic model
            return self._db_plan_to_pydantic(db_plan)
            
        except Exception as e:
            logger.error(f"Failed to get travel plan: {e}")
            raise
    
    async def list_travel_plans(self, skip: int = 0, limit: int = 10) -> Tuple[List[TravelPlan], int]:
        """List travel plans with pagination"""
        try:
            # Get total count
            count_result = await self.db.execute(select(TravelPlanModel))
            total = len(count_result.scalars().all())
            
            # Get paginated results
            result = await self.db.execute(
                select(TravelPlanModel)
                .offset(skip)
                .limit(limit)
                .order_by(TravelPlanModel.created_at.desc())
            )
            db_plans = result.scalars().all()
            
            # Convert to Pydantic models
            plans = [self._db_plan_to_pydantic(plan) for plan in db_plans]
            
            return plans, total
            
        except Exception as e:
            logger.error(f"Failed to list travel plans: {e}")
            raise
    
    async def delete_travel_plan(self, plan_id: str) -> bool:
        """Delete travel plan from database"""
        try:
            result = await self.db.execute(
                delete(TravelPlanModel).where(TravelPlanModel.id == plan_id)
            )
            await self.db.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"Failed to delete travel plan: {e}")
            await self.db.rollback()
            raise
    
    async def refresh_plan(self, plan_id: str) -> None:
        """Refresh travel plan with updated prices"""
        try:
            # Get existing plan
            plan = await self.get_travel_plan(plan_id)
            if not plan:
                logger.warning(f"Plan {plan_id} not found for refresh")
                return
            
            # Create new plan with updated prices
            new_plan = await self.create_travel_plan(plan.request)
            new_plan.plan_id = plan_id  # Keep same ID
            
            # Update database
            await self.store_plan(new_plan)
            
            logger.info(f"Travel plan refreshed: {plan_id}")
            
        except Exception as e:
            logger.error(f"Failed to refresh travel plan: {e}")
            raise
    
    def _db_plan_to_pydantic(self, db_plan: TravelPlanModel) -> TravelPlan:
        """Convert database model to Pydantic model"""
        # Convert flight options
        flight_options = [
            FlightOption(**flight_data) 
            for flight_data in db_plan.flight_options
        ]
        
        # Convert hotel options
        hotel_options = [
            HotelOption(**hotel_data) 
            for hotel_data in db_plan.hotel_options
        ]
        
        # Create request object
        request = TravelPlanRequest(
            destination=db_plan.destination,
            start_date=db_plan.start_date.date(),
            end_date=db_plan.end_date.date(),
            budget=db_plan.budget,
            travelers=db_plan.travelers,
            travel_class=db_plan.travel_class,
            hotel_category=db_plan.hotel_category,
            preferences=db_plan.preferences
        )
        
        return TravelPlan(
            plan_id=db_plan.id,
            request=request,
            total_cost=db_plan.total_cost,
            budget_utilization=db_plan.budget_utilization,
            flight_options=flight_options,
            hotel_options=hotel_options,
            recommendations=db_plan.recommendations,
            created_at=db_plan.created_at,
            expires_at=db_plan.expires_at
        )
    
    async def close(self):
        """Close service connections"""
        await self.flight_service.close()
        await self.hotel_service.close()
