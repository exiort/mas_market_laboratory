import sys

from environment import Environment

from simulation.core import SimulationInitializer



def main():
    if len(sys.argv) != 2:
        print(f"Invalid Usage! Correct Usage: 'python {sys.argv[0]} [someconfig.json]'")
        return

    if sys.argv[1][-5:] != ".json":
        print(f"Invalid Usage! Correct Usage: 'python {sys.argv[0]} [someconfig.json]'")
        return
        

    SimulationInitializer.INITIALIZE_CONFIGS(sys.argv[1])
    environment = Environment()

    
if __name__ == "__main__":
    main()
