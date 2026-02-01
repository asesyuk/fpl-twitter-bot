"""Feature 3: Daily stats summary."""

from . import fpl_api
from . import twitter


def format_number(n: int) -> str:
    """Format large numbers with K/M suffix."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)


def format_daily_stats_tweet(data: dict) -> str:
    """Format daily stats into a tweet."""
    transfers_in = fpl_api.get_top_transfers(data, limit=5)
    transfers_out = fpl_api.get_top_transfers_out(data, limit=5)
    most_owned = fpl_api.get_most_captained(data, limit=3)

    gw = fpl_api.get_current_gameweek(data["events"])
    gw_num = gw["id"] if gw else "?"

    lines = [f"📊 FPL Daily Update - GW{gw_num}\n"]

    lines.append("🔥 Top Transfers IN:")
    for p in transfers_in[:3]:
        lines.append(f"  {p['name']} ({p['team']}) - {format_number(p['transfers_in'])}")

    lines.append("\n❄️ Top Transfers OUT:")
    for p in transfers_out[:3]:
        lines.append(f"  {p['name']} ({p['team']}) - {format_number(p['transfers_out'])}")

    lines.append("\n👑 Most Selected:")
    for p in most_owned[:3]:
        lines.append(f"  {p['name']} ({p['team']}) - {p['selected_by']}%")

    lines.append("\n#FPL #FPLCommunity")

    return "\n".join(lines)


def run(dry_run: bool = False):
    """Post daily stats summary."""
    print("Generating daily stats...")

    data = fpl_api.get_bootstrap_static()
    tweet_text = format_daily_stats_tweet(data)
    twitter.post_tweet(tweet_text, dry_run=dry_run)


if __name__ == "__main__":
    run(dry_run=True)
