"""Feature 4: Gameweek results summary."""

from . import fpl_api
from . import twitter


def format_gameweek_results_tweet(data: dict) -> str | None:
    """Format gameweek results into a tweet."""
    events = data["events"]

    # Find the most recently finished gameweek
    finished_gw = None
    for event in events:
        if event["finished"]:
            finished_gw = event

    if not finished_gw:
        return None

    gw_num = finished_gw["id"]
    avg_score = finished_gw.get("average_entry_score", "N/A")
    highest_score = finished_gw.get("highest_score", "N/A")

    top_scorers = fpl_api.get_top_gameweek_scorers(data, limit=5)

    if not top_scorers:
        return None

    lines = [f"📈 Gameweek {gw_num} Results\n"]

    lines.append(f"📊 Average: {avg_score} pts")
    lines.append(f"🏆 Highest: {highest_score} pts\n")

    lines.append("⭐ Top Performers:")
    for p in top_scorers:
        lines.append(f"  {p['name']} ({p['team']}) - {p['points']} pts")

    lines.append(f"\n#FPL #FPLCommunity #GW{gw_num}")

    return "\n".join(lines)


def run(dry_run: bool = False):
    """Post gameweek results summary."""
    print("Generating gameweek results...")

    data = fpl_api.get_bootstrap_static()
    tweet_text = format_gameweek_results_tweet(data)

    if tweet_text:
        twitter.post_tweet(tweet_text, dry_run=dry_run)
    else:
        print("No finished gameweek data available")


if __name__ == "__main__":
    run(dry_run=True)
