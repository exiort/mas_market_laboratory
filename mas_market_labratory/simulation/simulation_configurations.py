from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

from market.market_structures.economy_scenario import EconomyScenario



class SimulationConfigurations(BaseSettings):
    PRICE_SCALE:int

    SIMULATION_MACRO_TICK:int
    SIMULATION_MICRO_TICK:int

    ECONOMY_SCENARIO:EconomyScenario

    model_config = SettingsConfigDict(frozen=True)


__SIMULATION_CONFIGURATION:Optional[SimulationConfigurations] = None


def get_simulation_configurations() -> SimulationConfigurations:
    assert __SIMULATION_CONFIGURATION is not None

    return __SIMULATION_CONFIGURATION
