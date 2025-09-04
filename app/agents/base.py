"""
Base agent configuration for CrewAI
"""

from crewai import Agent, Task, Crew
from typing import Dict, Any, List
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all CrewAI agents"""
    
    def __init__(self, name: str, role: str, goal: str, backstory: str):
        """
        Initialize base agent
        
        Args:
            name: Agent name
            role: Agent role
            goal: Agent goal
            backstory: Agent backstory
        """
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.agent = None
        self._create_agent()
    
    def _create_agent(self) -> None:
        """Create the CrewAI agent"""
        try:
            self.agent = Agent(
                name=self.name,
                role=self.role,
                goal=self.goal,
                backstory=self.backstory,
                verbose=True,
                allow_delegation=False,
                max_iter=3,
                memory=True
            )
            logger.info(f"Created agent: {self.name}")
        except Exception as e:
            logger.error(f"Failed to create agent {self.name}: {e}")
            raise
    
    def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> str:
        """
        Execute a task with the agent
        
        Args:
            task_description: Description of the task
            context: Additional context for the task
            
        Returns:
            Task execution result
        """
        try:
            task = Task(
                description=task_description,
                agent=self.agent,
                expected_output="Detailed response with actionable insights"
            )
            
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            logger.info(f"Task executed successfully by {self.name}")
            return str(result)
            
        except Exception as e:
            logger.error(f"Task execution failed for {self.name}: {e}")
            raise
