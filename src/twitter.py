"""Twitter/X API client for posting tweets."""

import os
import tweepy
from dotenv import load_dotenv

load_dotenv()


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
    """Post a tweet. If dry_run is True, just print instead."""
    if dry_run:
        print(f"[DRY RUN] Would tweet:\n{text}\n{'='*50}")
        return None

    client = get_client()
    response = client.create_tweet(text=text)
    print(f"Tweet posted: {response.data['id']}")
    return response.data


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
