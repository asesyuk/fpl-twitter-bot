"""FPL API client for fetching Fantasy Premier League data."""

import requests
from datetime import datetime, timezone

BASE_URL = "https://fantasy.premierleague.com/api"


def get_bootstrap_static():
    """Get main FPL data including players, teams, and gameweeks."""
    response = requests.get(f"{BASE_URL}/bootstrap-static/", timeout=30)
    response.raise_for_status()
    return response.json()


def get_player_by_id(players: list, player_id: int) -> dict | None:
    """Find a player by their ID."""
    for player in players:
        if player["id"] == player_id:
            return player
    return None


def get_team_name(teams: list, team_id: int) -> str:
    """Get team short name by ID."""
    for team in teams:
        if team["id"] == team_id:
            return team["short_name"]
    return "???"


def get_current_gameweek(events: list) -> dict | None:
    """Get the current or next gameweek."""
    for event in events:
        if event["is_current"]:
            return event
        if event["is_next"]:
            return event
    return None


def get_next_deadline(events: list) -> tuple[int, datetime] | None:
    """Get the next gameweek deadline."""
    for event in events:
        if event["is_next"] or (event["is_current"] and not event["finished"]):
            deadline_str = event["deadline_time"]
            deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
            return event["id"], deadline
    return None


def get_top_transfers(data: dict, limit: int = 5) -> list[dict]:
    """Get most transferred in players this gameweek."""
    players = data["elements"]
    sorted_players = sorted(players, key=lambda x: x["transfers_in_event"], reverse=True)
    teams = data["teams"]

    result = []
    for p in sorted_players[:limit]:
        result.append({
            "name": p["web_name"],
            "team": get_team_name(teams, p["team"]),
            "transfers_in": p["transfers_in_event"],
            "price": p["now_cost"] / 10,
        })
    return result


def get_top_transfers_out(data: dict, limit: int = 5) -> list[dict]:
    """Get most transferred out players this gameweek."""
    players = data["elements"]
    sorted_players = sorted(players, key=lambda x: x["transfers_out_event"], reverse=True)
    teams = data["teams"]

    result = []
    for p in sorted_players[:limit]:
        result.append({
            "name": p["web_name"],
            "team": get_team_name(teams, p["team"]),
            "transfers_out": p["transfers_out_event"],
            "price": p["now_cost"] / 10,
        })
    return result


def get_most_captained(data: dict, limit: int = 5) -> list[dict]:
    """Get most captained players."""
    players = data["elements"]
    # Filter to players with significant ownership
    popular = [p for p in players if p["selected_by_percent"] and float(p["selected_by_percent"]) > 5]
    # Sort by a proxy: high ownership + high points suggests captaincy
    sorted_players = sorted(popular, key=lambda x: float(x["selected_by_percent"]), reverse=True)
    teams = data["teams"]

    result = []
    for p in sorted_players[:limit]:
        result.append({
            "name": p["web_name"],
            "team": get_team_name(teams, p["team"]),
            "selected_by": p["selected_by_percent"],
            "total_points": p["total_points"],
        })
    return result


def get_top_gameweek_scorers(data: dict, limit: int = 5) -> list[dict]:
    """Get highest scoring players in the current/last gameweek."""
    players = data["elements"]
    sorted_players = sorted(players, key=lambda x: x["event_points"], reverse=True)
    teams = data["teams"]

    result = []
    for p in sorted_players[:limit]:
        if p["event_points"] > 0:
            result.append({
                "name": p["web_name"],
                "team": get_team_name(teams, p["team"]),
                "points": p["event_points"],
                "price": p["now_cost"] / 10,
            })
    return result


def get_average_score(events: list) -> int | None:
    """Get the average score for the current gameweek."""
    for event in events:
        if event["is_current"] and event["finished"]:
            return event["average_entry_score"]
        if event["is_previous"]:
            return event["average_entry_score"]
    return None


def get_highest_score(events: list) -> int | None:
    """Get the highest score for the current gameweek."""
    for event in events:
        if event["is_current"] and event["finished"]:
            return event["highest_score"]
        if event["is_previous"]:
            return event["highest_score"]
    return None
