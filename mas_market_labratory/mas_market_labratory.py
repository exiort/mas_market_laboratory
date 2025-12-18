import sys

from environment import Environment

#from simulation.simulation_realtime_data import __SIMULATION_REALTIME_DATA, SimulationRealTimeData



def main():
    if len(sys.argv) != 2:
        print(f"Invalid Usage! Correct Usage: 'python {sys.argv[0]} [someconfig.json]'")
        return

    if sys.argv[1][-5:] != ".json":
        print(f"Invalid Usage! Correct Usage: 'python {sys.argv[0]} [someconfig.json]'")
        return
        


if __name__ == "__main__":
    main()
