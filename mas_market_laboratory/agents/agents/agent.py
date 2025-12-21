from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from environment.views.account_view import AccountView
from intents import AgentIntent
from mas_market_laboratory.agents.models.agent_constants import AgentConstants
from models import AgentView, AgentFeedback



class Agent(ABC):
    agent_id:int
    account_view:AccountView
    constants:AgentConstants
    

    def __init__(self, agent_id:int, account_view:AccountView, constants:AgentConstants) -> None:
        super().__init__()

        self.agent_id = agent_id
        self.account_view = account_view
        self.constants = constants
        
        
    @abstractmethod
    def decide(self, view:AgentView) -> List[AgentIntent]:
        pass


    @abstractmethod
    def reflect(self, feedback:AgentFeedback) -> None:
        pass
