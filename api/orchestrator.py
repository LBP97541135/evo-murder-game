"""
EvoMap Murder Game - Global Orchestrator Singleton

将 AgentOrchestrator 实例放在独立模块中，避免 routes → main → orchestrator 的循环导入。
所有需要 orchestrator 的模块从此处导入。
"""

from api.agents.agent_orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
