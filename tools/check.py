import json
from pathlib import Path

from cardlib import PACKAGE_ROOT, search_cards, validate_bundle


def run_retrieval_cases(cards):
    path = PACKAGE_ROOT / "evals" / "retrieval_cases.yaml"
    suite = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    for case in suite["cases"]:
        results = search_cards(cards, case["query"], case.get("filters", {}))
        actual = [item["concept"] for item in results]
        for expected in case.get("expected", []):
            if expected not in actual:
                errors.append(f"{case['id']}: missing {expected}; actual={actual}")
        for group in case.get("expected_any", []):
            if not any(expected in actual for expected in group):
                errors.append(f"{case['id']}: none of {group}; actual={actual}")
        for excluded in case.get("excluded", []):
            if excluded in actual:
                errors.append(f"{case['id']}: excluded {excluded} was returned")
    return len(suite["cases"]), errors


def main():
    cards, errors = validate_bundle()
    case_count, eval_errors = run_retrieval_cases(cards)
    errors.extend(eval_errors)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print(f"PASS: {len(cards)} cards, indexes, sources, links and lifecycle rules")
    print(f"PASS: {case_count} retrieval cases")


if __name__ == "__main__":
    main()
