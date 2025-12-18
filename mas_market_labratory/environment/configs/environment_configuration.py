from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

from environment.configs.models import EconomyScenario



class EnvironmentConfiguation(BaseSettings):
    PRICE_SCALE:int
    DB_PATH:str
    
    INSIGHT_L2_DEPTH:int
    ECONOMY_SCENARIO:EconomyScenario
    
    model_config = SettingsConfigDict(frozen=True)


__ENVIRONMENT_CONFIGURATION:Optional[EnvironmentConfiguation] = None


def get_environment_configuration() -> EnvironmentConfiguation:
    assert __ENVIRONMENT_CONFIGURATION is not None

    return __ENVIRONMENT_CONFIGURATION
