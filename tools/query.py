import argparse
import json
import sys

from cardlib import load_cards, search_cards

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Search the standalone optimization knowledge bundle")
    parser.add_argument("query")
    parser.add_argument("--type", choices=["optimizations", "runbooks"])
    parser.add_argument("--platform")
    parser.add_argument("--status", choices=["stable", "draft", "deprecated", "all"], default="stable")
    parser.add_argument("-k", type=int, default=5)
    args = parser.parse_args()
    if args.k < 1:
        parser.error("k must be positive")
    filters = {"type": args.type, "platform": args.platform, "status": args.status, "k": args.k}
    results = search_cards(load_cards(), args.query, filters)
    print(json.dumps({"query": args.query, "count": len(results), "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
