"""
Base Agent Architecture for Multi-Agent AI System

Each agent works independently and communicates with the orchestration service.
Agents are autonomous, specialized, and can execute in parallel.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from utils.logger import logger


class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRole(str, Enum):
    """Different agent roles in the system"""
    RESEARCH = "research"
    SCRIPT = "script"
    THUMBNAIL = "thumbnail"
    SEO = "seo"
    VIDEO = "video"
    PUBLISHING = "publishing"
    ANALYTICS = "analytics"
    SCENE_DIRECTOR = "scene_director"
    VOICE = "voice"
    DUBBING = "dubbing"
    MUSIC = "music"


@dataclass
class AgentTask:
    """Task assigned to an agent"""
    task_id: str
    role: AgentRole
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    status: AgentStatus = AgentStatus.IDLE
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    
    Each agent:
    - Has a specific role and expertise
    - Executes tasks autonomously
    - Reports results back to orchestration service
    - Can delegate to other agents
    - Maintains learning state
    """
    
    def __init__(self, agent_id: str, role: AgentRole):
        self.agent_id = agent_id
        self.role = role
        self.status = AgentStatus.IDLE
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentTask] = []
        self.learning_state: Dict[str, Any] = {}
        
        logger.info(f"Agent {agent_id} ({role.value}) initialized")
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a task assigned to this agent"""
        self.current_task = task
        self.status = AgentStatus.THINKING
        
        try:
            logger.info(f"Agent {self.agent_id} executing task {task.task_id}")
            
            # Think phase
            analysis = await self._think(task.input_data)
            
            # Execution phase
            self.status = AgentStatus.EXECUTING
            result = await self._execute(analysis, task.input_data)
            
            # Learning phase
            await self._learn(task.input_data, result)
            
            # Update task
            task.output_data = result
            task.status = AgentStatus.COMPLETED
            task.completed_at = datetime.now()
            
            self.status = AgentStatus.COMPLETED
            logger.info(f"Agent {self.agent_id} completed task {task.task_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Agent {self.agent_id} failed on task {task.task_id}: {str(e)}")
            task.status = AgentStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            self.status = AgentStatus.FAILED
            raise
        
        finally:
            self.task_history.append(task)
    
    @abstractmethod
    async def _think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thinking phase - Agent analyzes input and plans approach
        
        Returns analysis/plan for execution
        """
        pass
    
    @abstractmethod
    async def _execute(self, analysis: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execution phase - Agent performs the actual work
        
        Returns execution results
        """
        pass
    
    @abstractmethod
    async def _learn(self, input_data: Dict[str, Any], result: Dict[str, Any]):
        """
        Learning phase - Agent updates its knowledge/state
        
        Used for continuous improvement and optimization
        """
        pass
    
    async def delegate_to_agent(self, other_agent: 'BaseAgent', task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate a sub-task to another agent
        
        Enables multi-agent collaboration
        """
        logger.info(f"Agent {self.agent_id} delegating to {other_agent.agent_id}")
        
        delegation_task = AgentTask(
            task_id=f"{self.current_task.task_id}_sub",
            role=other_agent.role,
            input_data=task_data,
            output_data={}
        )
        
        return await other_agent.execute_task(delegation_task)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "status": self.status.value,
            "current_task": self.current_task.task_id if self.current_task else None,
            "tasks_completed": len([t for t in self.task_history if t.status == AgentStatus.COMPLETED]),
            "learning_state_size": len(self.learning_state)
        }
    
    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get agent's task history"""
        return [
            {
                "task_id": t.task_id,
                "status": t.status.value,
                "created_at": t.created_at.isoformat(),
                "completed_at": t.completed_at.isoformat() if t.completed_at else None
            }
            for t in self.task_history[-limit:]
        ]


class AgentCoordinator:
    """
    Coordinates multiple agents working together on complex tasks.
    
    Manages:
    - Task distribution
    - Agent communication
    - Dependency resolution
    - Result aggregation
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.running_tasks: Dict[str, List[AgentTask]] = {}
        
        logger.info("Agent Coordinator initialized")
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the coordinator"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Agent {agent.agent_id} registered")
    
    async def orchestrate_parallel_tasks(self, tasks: List[AgentTask]) -> Dict[str, Dict[str, Any]]:
        """
        Execute multiple tasks in parallel across different agents
        
        Useful for multi-agent workflows where agents work independently
        """
        logger.info(f"Orchestrating {len(tasks)} parallel tasks")
        
        results = {}
        tasks_to_run = []
        
        for task in tasks:
            agent = self.agents.get(task.role.value)
            if agent:
                tasks_to_run.append(self._run_task_and_store(agent, task, results))
            else:
                logger.warning(f"No agent found for role {task.role.value}")
        
        await asyncio.gather(*tasks_to_run)
        return results
    
    async def _run_task_and_store(self, agent: BaseAgent, task: AgentTask, results: Dict):
        """Run a task and store the result"""
        try:
            result = await agent.execute_task(task)
            results[task.role.value] = result
        except Exception as e:
            logger.error(f"Task failed: {str(e)}")
            results[task.role.value] = {"error": str(e)}
    
    async def orchestrate_sequential_tasks(self, tasks: List[AgentTask]) -> Dict[str, Dict[str, Any]]:
        """
        Execute tasks sequentially with dependency resolution
        
        Later tasks can use output from earlier tasks
        """
        logger.info(f"Orchestrating {len(tasks)} sequential tasks")
        
        results = {}
        
        for task in tasks:
            agent = self.agents.get(task.role.value)
            if agent:
                # Pass previous results as context
                task.input_data["previous_results"] = results
                
                try:
                    result = await agent.execute_task(task)
                    results[task.role.value] = result
                except Exception as e:
                    logger.error(f"Task {task.task_id} failed: {str(e)}")
                    results[task.role.value] = {"error": str(e)}
                    break
            else:
                logger.warning(f"No agent found for role {task.role.value}")
        
        return results
    
    def get_all_agents_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered agents"""
        return {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }
    
    def get_coordinator_stats(self) -> Dict[str, Any]:
        """Get coordinator statistics"""
        total_agents = len(self.agents)
        total_tasks = sum(len(tasks) for tasks in self.running_tasks.values())
        
        return {
            "total_agents": total_agents,
            "agents_by_role": self._count_agents_by_role(),
            "running_tasks": total_tasks,
            "agents_status": self.get_all_agents_status()
        }
    
    def _count_agents_by_role(self) -> Dict[str, int]:
        """Count agents by role"""
        counts = {}
        for agent in self.agents.values():
            role = agent.role.value
            counts[role] = counts.get(role, 0) + 1
        return counts


# Global coordinator instance
_coordinator = None


def get_agent_coordinator() -> AgentCoordinator:
    """Get or create agent coordinator"""
    global _coordinator
    if _coordinator is None:
        _coordinator = AgentCoordinator()
    return _coordinator
