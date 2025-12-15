from typing import Optional
from mas_market_labratory.simulation.market.market_structures.economy_insight_view import EconomyInsightView



class SimulationRealTimeData:
    __macro_tick:int
    __micro_tick:int

    __simulation_macro_tick:int
    __simulation_micro_tick:int
    
    __economy_insight_view:EconomyInsightView
    __exchange_data:int


    def __init__(
            self,
            init_macro_tick:int,
            init_micro_tick:int,
            simulation_macro_tick:int,
            simulation_micro_tick:int,
            economy_insight:EconomyInsightView
    ) -> None:
        self.__macro_tick = init_macro_tick
        self.__micro_tick = init_micro_tick
        self.__simulation_macro_tick = simulation_macro_tick
        self.__simulation_micro_tick = simulation_micro_tick
        self.__economy_insight_view = economy_insight
        
    
    @property
    def MACRO_TICK(self) -> int:
        return self.__macro_tick


    @property
    def MICRO_TICK(self) -> int:
        return self.__micro_tick


    @property
    def ECONOMY_INSIGHT(self) -> EconomyInsightView:
        assert self.__economy_insight_view.macro_tick == self.__macro_tick

        return self.__economy_insight_view


    def step_hybrit_time(self) -> bool:
        self.__macro_tick += (self.__micro_tick + 1) // self.__simulation_micro_tick
        self.__micro_tick = (self.__micro_tick + 1) % self.__simulation_micro_tick

        if not self.__macro_tick < self.__simulation_macro_tick:
            return False

        return True

    def set_economy_insight(self, economy_insight:EconomyInsightView) -> None:
        assert economy_insight.macro_tick == self.__macro_tick

        self.__economy_insight_view = economy_insight


__SIMULATION_REALTIME_DATA:Optional[SimulationRealTimeData] = None


def get_simulation_realtime_data() -> SimulationRealTimeData:
    assert __SIMULATION_REALTIME_DATA is not None

    return __SIMULATION_REALTIME_DATA
