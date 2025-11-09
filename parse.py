import argparse
from src.orchestrator import Orchestrator
from src.strategies.stock_strategy import StockStrategy
from src.data.mongo_repository import StockMongoRepository

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["stock"], default="stock")
    parser.add_argument("--queries-file", default=None)
    args = parser.parse_args()

    strategy = StockStrategy()
    repo = StockMongoRepository()
    orch = Orchestrator(strategy, repo)
    orch.run_batch(args.queries_file)

if __name__ == "__main__":
    main()
