#!/usr/bin/env python3
"""编排 Agent"""

from core.agent.base import BaseAgent

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("Orchestrator")
        self.agents = {}
    
    def register_agent(self, name: str, agent):
        self.agents[name] = agent
    
    def process(self, user_input, context=None):
        if 'llm' in self.agents:
            return self.agents['llm'].process(user_input, context)
        return {"success": False, "error": "No agent available"}

orchestrator = OrchestratorAgent()
