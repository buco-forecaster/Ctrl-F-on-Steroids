import argparse
from src.orchestrator import Orchestrator
from src.strategies.stock_strategy import StockStrategy
from src.data.local_repository import LocalRepository

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["stock"], default="stock")
    parser.add_argument("--queries-file", default=None)
    parser.add_argument("--url", default="https://gemini.google.com/app")
    parser.add_argument("query", nargs="?", default=None)
    args = parser.parse_args()

    strategy = StockStrategy()
    repo = LocalRepository()
    orch = Orchestrator(strategy, repo)

    if args.queries_file:
        orch.run_batch(args.queries_file)
    elif args.query:
        orch.run_single(args.query, followups=[])
    else:
        orch.run_single("", followups=[])

if __name__ == "__main__":
    main()
