"""Twitter/X API client for posting tweets."""

import os
import time
import tweepy
from dotenv import load_dotenv

load_dotenv()

MAX_RETRIES = 3
RETRY_DELAY = 5


def get_client() -> tweepy.Client:
    """Get authenticated Twitter API v2 client."""
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    )
    return client


def post_tweet(text: str, dry_run: bool = False) -> dict | None:
    """Post a tweet with retry logic. If dry_run is True, just print instead."""
    if dry_run:
        print(f"[DRY RUN] Would tweet:\n{text}\n{'='*50}")
        return None

    client = get_client()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.create_tweet(text=text)
            print(f"Tweet posted: {response.data['id']}")
            return response.data
        except (tweepy.errors.Unauthorized, tweepy.errors.Forbidden) as e:
            print(f"Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                print(f"Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                print("All retries failed. Skipping tweet.")
                return None


def post_thread(tweets: list[str], dry_run: bool = False) -> list[dict]:
    """Post a thread of tweets."""
    if dry_run:
        print("[DRY RUN] Would post thread:")
        for i, tweet in enumerate(tweets, 1):
            print(f"  [{i}] {tweet}")
        print("=" * 50)
        return []

    client = get_client()
    results = []
    reply_to_id = None

    for tweet in tweets:
        if reply_to_id:
            response = client.create_tweet(text=tweet, in_reply_to_tweet_id=reply_to_id)
        else:
            response = client.create_tweet(text=tweet)

        results.append(response.data)
        reply_to_id = response.data["id"]
        print(f"Tweet posted: {reply_to_id}")

    return results
