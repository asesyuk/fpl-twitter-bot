#!/usr/bin/env python3
"""FPL Twitter Bot - Main entry point."""

import argparse
import sys

from src import price_changes
from src import deadlines
from src import daily_stats
from src import gameweek_results


def main():
    parser = argparse.ArgumentParser(description="FPL Twitter Bot")
    parser.add_argument(
        "command",
        choices=["price-changes", "deadline", "daily-stats", "gw-results", "all"],
        help="Which feature to run",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print tweets instead of posting",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force action (e.g., send deadline reminder regardless of time)",
    )

    args = parser.parse_args()

    if args.command == "price-changes":
        price_changes.run(dry_run=args.dry_run)

    elif args.command == "deadline":
        deadlines.run(dry_run=args.dry_run, force=args.force)

    elif args.command == "daily-stats":
        daily_stats.run(dry_run=args.dry_run)

    elif args.command == "gw-results":
        gameweek_results.run(dry_run=args.dry_run)

    elif args.command == "all":
        print("Running all features...")
        print("\n--- Price Changes ---")
        price_changes.run(dry_run=args.dry_run)
        print("\n--- Deadline Check ---")
        deadlines.run(dry_run=args.dry_run)
        print("\n--- Daily Stats ---")
        daily_stats.run(dry_run=args.dry_run)
        print("\n--- GW Results ---")
        gameweek_results.run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
