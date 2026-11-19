import pytest

from microcoach.metrics import compute_snapshot


def make_game(**overrides):
    data = {
        "activePlayer": {
            "summonerName": "Me",
            "riotId": "Me#EUW",
            "level": 9,
            "currentGold": 850,
        },
        "allPlayers": [
            {
                "summonerName": "Other",
                "riotId": "Other#EUW",
                "championName": "Garen",
                "scores": {"kills": 9, "deaths": 0, "assists": 1, "creepScore": 200},
            },
            {
                "summonerName": "Me",
                "riotId": "Me#EUW",
                "championName": "Ahri",
                "scores": {"kills": 4, "deaths": 2, "assists": 6, "creepScore": 120},
            },
        ],
        "gameData": {"gameTime": 600.0},
    }
    data.update(overrides)
    return data


def test_reads_scores_and_champion_for_the_active_player():
    snap = compute_snapshot(make_game())
    assert snap.champion_name == "Ahri"
    assert (snap.kills, snap.deaths, snap.assists, snap.cs) == (4, 2, 6, 120)
    assert snap.cs_per_min == pytest.approx(12.0)
    assert snap.level == 9
    assert snap.current_gold == 850


def test_falls_back_to_scores_on_active_player():
    game = make_game(allPlayers=[])
    game["activePlayer"]["scores"] = {"kills": 1, "deaths": 1, "assists": 1, "creepScore": 30}
    snap = compute_snapshot(game)
    assert snap.cs == 30
    assert snap.champion_name == "Unknown"


def test_missing_active_player_returns_none():
    assert compute_snapshot({"allPlayers": []}) is None
    assert compute_snapshot({"activePlayer": "oops"}) is None


def test_non_dict_payload_returns_none():
    assert compute_snapshot(None) is None
    assert compute_snapshot([]) is None


def test_malformed_values_do_not_raise():
    game = make_game()
    game["activePlayer"]["level"] = "n/a"
    game["activePlayer"]["currentGold"] = None
    game["gameData"]["gameTime"] = "soon"
    game["allPlayers"][1]["scores"] = {"kills": "x", "creepScore": None}
    snap = compute_snapshot(game)
    assert snap.level == 0
    assert snap.current_gold == 0
    assert snap.game_time == 0.0
    assert snap.kills == 0 and snap.cs == 0

