"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

# Support both `python src/main.py` (src/ on the path) and
# `python -m src.main` (run as a package from the repo root).
try:
    from src.recommender import load_songs, recommend_songs
except ModuleNotFoundError:
    from recommender import load_songs, recommend_songs


# Numeric values are raw here; recommend_songs normalizes them to 0-1 using
# the library's per-feature ranges before scoring.
PROFILES = [
    # A "deep-focus / chill lofi" listener.
    ("DEEP-FOCUS LOFI", {
        "genre": "lofi",
        "mood": "focused",
        "energy": 0.40,
        "tempo_bpm": 76,
        "valence": 0.55,
        "danceability": 0.60,
        "acousticness": 0.75,
        "instrumentalness": 0.90,
        "popularity": 50,
    }),
    # An upbeat "pop / happy" listener (the starter default).
    ("UPBEAT POP", {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.80,
        "tempo_bpm": 118,
        "valence": 0.85,
        "danceability": 0.80,
        "acousticness": 0.20,
        "instrumentalness": 0.05,
        "popularity": 75,
    }),
]


def show_recommendations(label: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print the top-k recommendations for one profile as a set of cards."""
    divider = "-" * 46
    print(f"\nTOP RECOMMENDATIONS - {label}")
    print(f"Profile: {user_prefs['genre']} / {user_prefs['mood']}"
          f"  |  target energy {user_prefs['energy']:.2f}")
    print("=" * 46)
    print()
    for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k), start=1):
        # Rank on the left, score right-aligned.
        print(f"{'#' + str(rank):<34}Score: {score:.2f}")
        print(f"    {'Song:':<8}{song['title']}")
        print(f"    {'Artist:':<8}{song['artist']}")
        print(f"    {'Genre:':<8}{song['genre']}")
        print(f"    {'Mood:':<8}{song['mood']}")
        print()
        print("    Why:")
        # recommend_songs joins the reasons with '; '; split them back out so
        # each reason (with its point contribution) sits on its own line.
        for reason in explanation.split("; "):
            print(f"      - {reason}")
        print(divider)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for label, user_prefs in PROFILES:
        show_recommendations(label, user_prefs, songs, k=5)


if __name__ == "__main__":
    main()
