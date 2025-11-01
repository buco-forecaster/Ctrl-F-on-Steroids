import argparse
from src.orchestrator import Orchestrator
from src.strategies.stock_strategy import StockStrategy
from src.data.local_repository import LocalRepository

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["stock"], default="stock")
    parser.add_argument("--queries-file", default=None)
    args = parser.parse_args()

    strategy = StockStrategy()
    repo = LocalRepository()
    orch = Orchestrator(strategy, repo)
    orch.run_batch(args.queries_file)

if __name__ == "__main__":
    main()
