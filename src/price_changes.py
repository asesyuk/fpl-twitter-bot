"""Feature 1: Price change alerts."""

import json
import os
from pathlib import Path

from . import fpl_api
from . import twitter

DATA_DIR = Path(__file__).parent.parent / "data"
PRICES_FILE = DATA_DIR / "prices.json"


def load_previous_prices() -> dict:
    """Load previously stored prices."""
    if PRICES_FILE.exists():
        with open(PRICES_FILE) as f:
            return json.load(f)
    return {}


def save_current_prices(prices: dict):
    """Save current prices for comparison."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(PRICES_FILE, "w") as f:
        json.dump(prices, f)


def get_current_prices(data: dict) -> dict:
    """Extract current prices from FPL data."""
    prices = {}
    for player in data["elements"]:
        prices[str(player["id"])] = {
            "name": player["web_name"],
            "team": fpl_api.get_team_name(data["teams"], player["team"]),
            "price": player["now_cost"],
        }
    return prices


def find_price_changes(old_prices: dict, new_prices: dict) -> tuple[list, list]:
    """Find players whose prices have changed."""
    risers = []
    fallers = []

    for player_id, new_data in new_prices.items():
        if player_id in old_prices:
            old_price = old_prices[player_id]["price"]
            new_price = new_data["price"]

            if new_price > old_price:
                risers.append({
                    "name": new_data["name"],
                    "team": new_data["team"],
                    "old_price": old_price / 10,
                    "new_price": new_price / 10,
                    "change": (new_price - old_price) / 10,
                })
            elif new_price < old_price:
                fallers.append({
                    "name": new_data["name"],
                    "team": new_data["team"],
                    "old_price": old_price / 10,
                    "new_price": new_price / 10,
                    "change": (old_price - new_price) / 10,
                })

    return risers, fallers


def format_price_tweet(risers: list, fallers: list) -> str | None:
    """Format price changes into a tweet."""
    if not risers and not fallers:
        return None

    lines = ["📊 FPL Price Changes\n"]

    if risers:
        lines.append("📈 RISERS:")
        for p in risers[:5]:  # Limit to 5 to fit in tweet
            lines.append(f"  {p['name']} ({p['team']}) £{p['new_price']:.1f}m (+£{p['change']:.1f}m)")

    if fallers:
        if risers:
            lines.append("")
        lines.append("📉 FALLERS:")
        for p in fallers[:5]:
            lines.append(f"  {p['name']} ({p['team']}) £{p['new_price']:.1f}m (-£{p['change']:.1f}m)")

    lines.append("\n#FPL #FPLCommunity")

    return "\n".join(lines)


def run(dry_run: bool = False):
    """Check for price changes and tweet if any found."""
    print("Checking for price changes...")

    data = fpl_api.get_bootstrap_static()
    current_prices = get_current_prices(data)
    previous_prices = load_previous_prices()

    if not previous_prices:
        print("No previous prices found. Saving current prices for next run.")
        save_current_prices(current_prices)
        return

    risers, fallers = find_price_changes(previous_prices, current_prices)

    if risers or fallers:
        print(f"Found {len(risers)} risers and {len(fallers)} fallers")
        tweet_text = format_price_tweet(risers, fallers)
        if tweet_text:
            twitter.post_tweet(tweet_text, dry_run=dry_run)
    else:
        print("No price changes detected")

    # Always save current prices for next comparison
    save_current_prices(current_prices)


if __name__ == "__main__":
    run(dry_run=True)
