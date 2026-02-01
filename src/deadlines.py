"""Feature 2: Gameweek deadline reminders."""

from datetime import datetime, timezone, timedelta

from . import fpl_api
from . import twitter


def format_time_until(deadline: datetime) -> str:
    """Format the time remaining until deadline."""
    now = datetime.now(timezone.utc)
    diff = deadline - now

    if diff.total_seconds() < 0:
        return "PASSED"

    hours = int(diff.total_seconds() // 3600)
    minutes = int((diff.total_seconds() % 3600) // 60)

    if hours > 24:
        days = hours // 24
        hours = hours % 24
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def should_send_reminder(deadline: datetime) -> tuple[bool, str]:
    """Check if we should send a reminder based on time until deadline."""
    now = datetime.now(timezone.utc)
    diff = deadline - now
    hours_until = diff.total_seconds() / 3600

    # Send reminders at specific intervals
    if 23.5 < hours_until <= 24.5:
        return True, "24 hours"
    elif 5.5 < hours_until <= 6.5:
        return True, "6 hours"
    elif 0.5 < hours_until <= 1.5:
        return True, "1 hour"

    return False, ""


def format_deadline_tweet(gameweek: int, deadline: datetime, reminder_type: str) -> str:
    """Format a deadline reminder tweet."""
    deadline_str = deadline.strftime("%A %d %B at %H:%M GMT")
    time_until = format_time_until(deadline)

    tweet = f"""⏰ DEADLINE REMINDER

Gameweek {gameweek} deadline in {reminder_type}!

📅 {deadline_str}
⏳ {time_until} remaining

Make your transfers and set your captain!

#FPL #FPLCommunity #GW{gameweek}"""

    return tweet


def run(dry_run: bool = False, force: bool = False):
    """Check if deadline reminder should be sent and post if so."""
    print("Checking deadline...")

    data = fpl_api.get_bootstrap_static()
    result = fpl_api.get_next_deadline(data["events"])

    if not result:
        print("No upcoming deadline found")
        return

    gameweek, deadline = result
    print(f"Next deadline: GW{gameweek} at {deadline}")

    should_remind, reminder_type = should_send_reminder(deadline)

    if should_remind or force:
        if force:
            reminder_type = format_time_until(deadline)
        tweet_text = format_deadline_tweet(gameweek, deadline, reminder_type)
        twitter.post_tweet(tweet_text, dry_run=dry_run)
    else:
        time_until = format_time_until(deadline)
        print(f"No reminder needed right now. Deadline in {time_until}")


if __name__ == "__main__":
    run(dry_run=True, force=True)
